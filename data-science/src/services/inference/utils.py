import cv2
import yt_dlp
import numpy as np
import torch
import requests
from time import time
from urllib.parse import urlparse
from requests.auth import HTTPDigestAuth

def get_device():
    if not torch.cuda.is_available():
        return 'cpu'

    best_gpu = None
    max_free_mem = 0

    for i in range(torch.cuda.device_count()):
        free_mem = torch.cuda.mem_get_info(i)[0]  # mem_get_info returns (free, total)
        if free_mem > max_free_mem:
            max_free_mem = free_mem
            best_gpu = i

    return best_gpu

def frame_resize(frame, target_size: int = 640):
    original_height, original_width = frame.shape[:2]
    aspect_ratio = original_width / original_height

    if aspect_ratio > 1:
        new_width = target_size
        new_height = int(target_size / aspect_ratio)
    else:
        new_height = target_size
        new_width = int(target_size * aspect_ratio)

    resized_frame = cv2.resize(frame, (new_width, new_height))
    output_frame = np.zeros((target_size, target_size, 3), dtype=np.uint8)

    x_offset = (target_size - new_width) // 2
    y_offset = (target_size - new_height) // 2

    output_frame[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_frame

    # output_frame = cv2.flip(output_frame, 0)
    # output_frame = cv2.flip(output_frame, 1)

    return output_frame

def reformat_box(box, models_names):
    cls = str(int(box[-1]))
    model_id, class_id = int(cls[0]), int(cls[1:])
    x1, y1, x2, y2 = map(int, box[:4])
    conf = round(float(box[-2]), 2)
    label = models_names[model_id - 1][class_id]
    track_id = int(box[-3]) if len(box) == 7 else None

    return [x1, y1, x2, y2, conf, label, track_id]

def youtube_cap(source):
    with yt_dlp.YoutubeDL({'quiet': True, 'format': 'best'}) as ydl:
        info = ydl.extract_info(source, download=False)
        video_url = info['url']
    return cv2.VideoCapture(video_url)

class ThetaCap:
    def __init__(self, url, chunk_size=1024 * 75):
        parsed = urlparse(url)

        try:
            self.response = requests.post(
                url=f"{parsed.scheme}://{parsed.hostname}{parsed.path}",
                auth = HTTPDigestAuth(parsed.username, parsed.password),
                json={"name": "camera.getLivePreview"},
                headers={"Content-Type": "application/json;charset=utf-8"},
                stream=True,
                timeout=10
            )
            self.response.raise_for_status()
            self.stream = self.response.iter_content(chunk_size=chunk_size)

            self.buffer = b""
            self.last_timestamp = time()
            self.fps_estimate = 0.0
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            self.response = None
            self.stream = None

    def grab(self):
        """Advance to the next frame without decoding."""
        if not self.stream:
            return False

        try:
            chunk = next(self.stream)
        except StopIteration:
            return False

        if not chunk:
            return False

        self.buffer += chunk
        start = self.buffer.find(b'\xff\xd8')
        end = self.buffer.find(b'\xff\xd9')

        if start != -1 and end != -1 and end > start:
            self.jpg_data = self.buffer[start:end+2]
            self.buffer = self.buffer[end+2:]
            return True

        return False

    def read(self):
        """Get and decode the next frame."""
        if self.grab():
            frame = cv2.imdecode(np.frombuffer(self.jpg_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is not None:
                self.fps_estimate = 1.0 / ((current_time := time()) - self.last_timestamp)
                self.last_timestamp = current_time
                return True, frame

        return False, None

    def release(self):
        """Close the stream."""
        if self.response:
            self.response.close()
            self.response = None
            self.stream = None

    def get(self, _):
        """Return estimated frames per second."""
        return round(self.fps_estimate, 2)
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time as curr_time

from ultralytics import YOLO
from boxmot.tracker_zoo import create_tracker, get_tracker_config
from .utils import *

import math
from pathlib import Path
import base64

from config import NUM_PATCHES


class Predict:
    def __init__(self, sources: dict, models: dict):
        self.max_models = 4
        self.device = get_device()
        self.models_format = "onnx" if self.device == 'cpu' else "engine"
        self.processing_rate = np.inf
        print("Detected device:", self.device)

        assert 0 < len(sources) <= NUM_PATCHES, MemoryError(f"There must be at least one source. and can not process more than {NUM_PATCHES} sources at a channel.")
        assert 0 < len(models) <= self.max_models, MemoryError(f"There must be at least one model. and can not process more than {self.max_models} models at a channel.")
        
        self.sources = dict()
        self.models = dict()

        self.configure_inference()
        self.config_tracker()

        for name, source in sources.items():
            self.append_source(name, source)

        for name, parameters in models.items():
            self.append_model(name, parameters)

        self.sources_executor = ThreadPoolExecutor(max_workers=NUM_PATCHES)
        self.models_executor = ThreadPoolExecutor(max_workers=self.max_models)
   
    def __del__(self):
        self.models_executor.shutdown(wait=True)
        self.sources_executor.shutdown(wait=True)
        for source in list(self.sources.values()):
            source["captures"].release()

    def append_source(self, name:str, source:str):
        assert len(self.sources) < NUM_PATCHES, RuntimeError(f"Can't append this source, maximum is {NUM_PATCHES}")
        assert name not in self.sources.keys(), RuntimeError(f"Source {name}, is already exist. you cant add same source twice")
        
        cap = youtube_cap(source) if "youtu" in source else ThetaCap(source) if "http" in source else cv2.VideoCapture(source)
        # cap.set(cv2.CAP_PROP_CONVERT_RGB, 1)
        self.sources[name] = {
            "captures": cap,
            "tracker": create_tracker(**self.tracker_configurations) if self.tracker_configurations["tracker_type"] else None,
            "data": {
                "frame": None,
                "boxes": [],
                "masks": [],
                "keypoints": [],
                "frame_rate": cap.get(cv2.CAP_PROP_FPS)
            }
        }
        print(f"Source {name} added successfully")

    def delete_source(self, name:str):
        if name not in self.sources.keys():
            raise RuntimeError(f"Source {name} is not exist")
        
        del self.sources[name]

    def append_model(self, name:str, parameters:dict):
        if len(self.models) >= self.max_models:
            raise RuntimeError(f"Can't append this model, maximum is {self.max_models}")
        if name in self.models.keys():
            raise RuntimeError(f"Model {name}, is already exist. you can't add same model twice")
        
        model_path = f"static/models/{self.models_format}/{name + ' ' + parameters["task"] + ' ' + parameters["weight"]}.{self.models_format}"
        task = {"detection": "detect", "segmentation": "segment", "estimation": "pose"}.get(parameters["task"])
        self.models[name] = {
            "task": parameters["task"],
            "weight": parameters["weight"],
            "predictor": YOLO(model=model_path, task=task),
            "results": None
        }
        print(f"Model {model_path.split("/")[-1]} loaded successfully")

    def delete_model(self, name:str):
        if name not in self.models.keys():
            raise RuntimeError(f"Model {name} is not exist")
        
        del self.models[name]

    def configure_inference(self, confidence_threshold: float = 0.25, overlapping_threshold: float = 0.75,
                            augmentation_mode: bool = True, realtime_mode: bool = True):
        
        assert 0 <= confidence_threshold <= 1, ValueError("Confidence should be in range from 0 to 1")
        assert 0 <= overlapping_threshold <= 1, ValueError("iou_for_nms should be in range from 0 to 1")
        
        self.inference_configurations = {
            'conf': confidence_threshold,
            'iou': overlapping_threshold,
            'augment': augmentation_mode,
            'agnostic_nms': True,
            'half': not self.device == "cpu",
            'device': self.device,
            'verbose': False,
            'batch': NUM_PATCHES,
        }
        self.realtime_mode = realtime_mode

    def config_tracker(self, tracking: bool = True, reid: bool = False):

        tracker_type = None if not tracking else "ocsort" if not reid else "deepocsort"
           
        self.tracker_configurations = {
            "tracker_type": tracker_type,
            "tracker_config": get_tracker_config(tracker_type),
            "reid_weights": Path(f"static/models/reid/osnet_x1_0_market1501.pt") if reid else None,
            "device": self.device,
            "half": not self.device == "cpu",
            # "per_class": True,
        }
        
        for source in self.sources.values():
            source["tracker"] = create_tracker(**self.tracker_configurations) if tracking else None

    def load_frames(self):
        def single_loading(name, source):
            original_frame_rate = source["captures"].get(cv2.CAP_PROP_FPS)
            stride = max(1, math.ceil(original_frame_rate / self.processing_rate)) if self.realtime_mode else 1
            for _ in range(stride-1):
                if not source["captures"].grab():
                    source["captures"].release()
                    del self.sources[name]
                    break
            else:
                success, frame = source["captures"].read()
                if success:
                    source["data"]["frame"] = frame_resize(frame)
                    source["data"]["frame_rate"] = round(original_frame_rate / stride, 2)
                else:
                    source["captures"].release()
                    del self.sources[name]

        futures = [self.sources_executor.submit(single_loading, name, source) for name, source in list(self.sources.items())]
        for future in as_completed(futures):
            future.result()

    def process_frames(self):
        def single_processing(model, frames):
            model["results"] = model["predictor"].predict(source=frames, **self.inference_configurations)

        frames = [source["data"]["frame"] for source in self.sources.values()] 
        frames.extend([np.zeros((640, 640, 3), dtype=np.uint8) for _ in range(NUM_PATCHES - len(self.sources))])

        futures = [self.models_executor.submit(single_processing, model, frames) for model in self.models.values()]
        for future in as_completed(futures):
            future.result()

    def run(self):
        start_time = curr_time()
        
        self.load_frames()
        self.process_frames()

        def process_models_result_for_source(source_index, source):
            models_names = []
            concatenated_boxes, concatenated_masks, concatenated_keypoints = [], [], []
            for model_index, model in enumerate(self.models.values(), start=1):
                results = model["results"][source_index]
                
                if results.boxes:
                    boxes = np.array([b.tolist() for b in list(results.boxes.data)])
                    boxes[:, -1] = [int(f"{model_index}{int(cls)}") for cls in boxes[:, -1]]
                    concatenated_boxes.append(boxes)
                
                if results.masks:
                    concatenated_masks.extend([m.astype(int).tolist() for m in results.masks.xy])
                
                if results.keypoints and results.keypoints.xy.size(1):
                    concatenated_keypoints.extend([[[int(x), int(y)] for x, y in k.tolist()] for k in results.keypoints.xy])
                
                models_names.append(model["predictor"].names)

            if concatenated_boxes:
                concatenated_boxes = np.concatenate(concatenated_boxes, axis=0)
                if source["tracker"]:
                    tracker = source["tracker"].update(concatenated_boxes, source["data"]["frame"])
                    if tracker.any():
                        concatenated_boxes = tracker[:, :-1]

                concatenated_boxes = [reformat_box(box, models_names) for box in concatenated_boxes]
            
            source["data"]["boxes"] = concatenated_boxes
            source["data"]["masks"] = concatenated_masks
            source["data"]["keypoints"] = concatenated_keypoints
            source["data"]["frame"] = base64.b64encode(cv2.imencode('.jpg', source["data"]["frame"])[1]).decode('utf-8')
        
        futures = [self.sources_executor.submit(process_models_result_for_source, source_index, source) for source_index, source in enumerate(self.sources.values())]
        for future in as_completed(futures):
            future.result()

        self.processing_rate = round(1/(curr_time() - start_time), 2)

        return [{"source_name": name, **source["data"]} for name, source in self.sources.items()]

if __name__ == '__main__':
    test = Predict(sources={
        "https:/Youtube/Gr0HpDM8Ki8": "https://youtu.be/Gr0HpDM8Ki8",
        "https:/Youtube/wqctLW0Hb_0": "https://youtu.be/wqctLW0Hb_0",
        # "rtsp:/Channel/201": "rtsp://admin:Meapal55@10.100.103.5:554/Streaming/Channels/201"
    },
    models={
        "Default": {
            "task": "detection",
            "weight": "nano"
        },
        "Default": {
            "task": "segmentation",
            "weight": "nano"
        },
        "Pose": {
            "task": "estimation",
            "weight": "nano"
        }
    }
    )

    test.config_tracker(0)

    while True:
        print(test.run_pipline())

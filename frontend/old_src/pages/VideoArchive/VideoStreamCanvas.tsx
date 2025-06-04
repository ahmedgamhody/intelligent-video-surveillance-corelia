import { useEffect, useRef } from "react";

interface IVideoStreamProps {
  stream: {
    name: string;
    frame: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    boxes: [number, number, number, number, number, string, any?][];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    masks: any[];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    keypoints: any[];
    meta: {
      frame_rate: number;
      skip_frames: number;
    };
  };
}

export default function VideoStream({ stream }: IVideoStreamProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const image = new Image();
    image.src = `data:image/jpeg;base64,${stream.frame}`;

    image.onload = () => {
      canvas.width = image.width;
      canvas.height = image.height;

      // draw image
      ctx.drawImage(image, 0, 0, image.width, image.height);

      // draw boxes
      stream.boxes.forEach((box) => {
        const [x1, y1, x2, y2, score, label] = box;

        ctx.strokeStyle = "red";
        ctx.lineWidth = 2;
        ctx.strokeRect(
          Number(x1),
          Number(y1),
          Number(x2) - Number(x1),
          Number(y2) - Number(y1)
        );

        ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
        ctx.fillRect(Number(x1), Number(y1) - 20, 100, 20);

        ctx.fillStyle = "white";
        ctx.font = "12px Arial";
        ctx.fillText(
          `${label} (${Math.round(Number(score) * 100)}%)`,
          Number(x1) + 4,
          Number(y1) - 6
        );
      });
    };
  }, [stream]);

  return (
    <div className="relative shadow-lg rounded-xl overflow-hidden">
      <canvas ref={canvasRef} className="w-full h-auto" />
      <div className="absolute top-2 left-2 bg-black bg-opacity-60 text-white text-sm px-2 py-1 rounded">
        {stream.name}
      </div>
    </div>
  );
}

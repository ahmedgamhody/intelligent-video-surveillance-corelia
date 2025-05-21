import { useEffect, useRef, useState } from "react";
import { IFrameData } from "../../interfaces";
import { PlotsConditionsType } from "../../types";

export default function FrameItem({
  frame,
  plotsConditions,
}: {
  frame: IFrameData;
  plotsConditions: PlotsConditionsType;
}) {
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        const { offsetWidth, offsetHeight } = containerRef.current;
        setDimensions({ width: offsetWidth, height: offsetHeight });
      }
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const originalSize = 640;

  return (
    <div className="bg-white rounded shadow p-2">
      {plotsConditions?.sourceName && (
        <p className="text-sm font-semibold mb-2">{frame?.source_name}</p>
      )}

      <div
        ref={containerRef}
        className="relative w-full aspect-square overflow-hidden"
      >
        <img
          src={`data:image/jpeg;base64,${frame?.frame}`}
          alt="frame"
          className="w-full h-full object-cover rounded"
        />
        {dimensions.width > 0 &&
          plotsConditions?.boxes &&
          frame?.boxes?.map((box, i) => {
            const [x1, y1, x2, y2, confidence, label] = box;
            const scaleX = dimensions.width / originalSize;
            const scaleY = dimensions.height / originalSize;
            const width = (x2 - x1) * scaleX;
            const height = (y2 - y1) * scaleY;

            return (
              <div
                key={i}
                className="absolute border-2 border-red-600 text-xs text-white font-bold bg-black bg-opacity-50 px-1 rounded"
                style={{
                  left: `${x1 * scaleX}px`,
                  top: `${y1 * scaleY}px`,
                  width: `${width}px`,
                  height: `${height}px`,
                }}
              >
                {plotsConditions?.classes && label}
                {plotsConditions?.confidence && (
                  <span> ({(confidence * 100).toFixed(1)}%)</span>
                )}
              </div>
            );
          })}
      </div>
    </div>
  );
}

import { useEffect, useState } from "react";
import SourceSkeleton from "../../ui/skeletons/SourceSkeleton";
import {
  CalendarDays,
  CirclePause,
  CloudDownload,
  Disc,
  Expand,
  Gauge,
  Grid2x2,
  Grid3x3,
  Table2,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import { Progress } from "flowbite-react";
import { useAppSelector } from "../../store/hooks";
import { IFrameData, IWSResponse } from "../../interfaces";
import FrameItem from "./Frame";
import { PlotsConditionsType } from "../../types";

export default function HomePage({
  plotsConditions,
}: {
  plotsConditions: PlotsConditionsType;
}) {
  const [itemsPerRow, setItemsPerRow] = useState(3);
  const [frames, setFrames] = useState<IFrameData[]>([]);
  const [isFirstItemExpanded, setIsFirstItemExpanded] = useState(false);
  const { selectedChannel } = useAppSelector((state) => state.channels);

  const getGridColsClass = () => {
    switch (itemsPerRow) {
      case 2:
        return "grid-cols-2";
      case 3:
      default:
        return "grid-cols-3";
    }
  };
// `ws://10.100.102.6:2345/ivs/v5/streamer/connect_channel?channel_name=${selectedChannel}`
  useEffect(() => {
    let socket: WebSocket | null = null;

    if (selectedChannel) {
      socket = new WebSocket(
        `ws://10.100.102.6:2345/ivs/v5/predictor/connect_channel?channel_name=${selectedChannel}`
        
      );
      socket.onmessage = (event) => {
        const res: IWSResponse[] = JSON.parse(event.data);
        const allFrameData = res.flatMap((entry) => entry.data);
        setFrames(allFrameData);
        console.log(res);
      };
      socket.onclose = () => {
        console.log("WebSocket closed");
      };
    }
    return () => {
      socket?.close();
    };
  }, [selectedChannel]);

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Scrollable Main Content */}
      <main className="flex-1 overflow-y-auto p-5">
        <div
          className={`grid gap-4 ${getGridColsClass()}`}
          style={{ gridAutoRows: "minmax(120px, auto)" }}
        >
          {frames.length === 0
            ? Array.from({ length: 8 }).map((_, index) => (
                <div
                  key={index}
                  className={
                    isFirstItemExpanded && index === 0
                      ? "col-span-2 row-span-2 h-[200%] bg-gray-100 rounded-lg"
                      : ""
                  }
                >
                  <SourceSkeleton />
                </div>
              ))
            : frames.map((frame, index) => (
                <div
                  key={index}
                  className={
                    isFirstItemExpanded && index === 0
                      ? "col-span-2 row-span-2 h-[200%] bg-gray-100 rounded-lg"
                      : isFirstItemExpanded &&
                        index === 1 &&
                        frames.length === 2
                      ? "col-start-3 row-start-1"
                      : ""
                  }
                >
                  <FrameItem frame={frame} plotsConditions={plotsConditions} />
                </div>
              ))}
        </div>
      </main>

      {/* Sticky Footer at Bottom */}
      <footer className="bg-gray-300 text-black p-3 flex flex-col gap-5">
        <div className="flex justify-between">
          <div className="flex items-center gap-2">
            <CalendarDays />
            <p className="sm:text-xs md:text-xs lg:text-sm">
              2025-04-12 08:00:00 AM
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Grid2x2
              className="cursor-pointer"
              onClick={() => {
                setItemsPerRow(2);
                setIsFirstItemExpanded(false);
              }}
            />
            <Grid3x3
              className="cursor-pointer"
              onClick={() => {
                setItemsPerRow(3);
                setIsFirstItemExpanded(false);
              }}
            />
            <Table2
              className="rotate-180 cursor-pointer"
              onClick={() => {
                setIsFirstItemExpanded(!isFirstItemExpanded);
                setItemsPerRow(3);
              }}
            />
          </div>
          <div className="flex items-center gap-2">
            <p className="sm:text-xs md:text-xs lg:text-sm">
              Preprocessing rate: 9.4 FPS
            </p>
            <Disc />
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <CirclePause className="cursor-pointer" />
            <Gauge className="cursor-pointer" />
            <ZoomIn className="cursor-pointer" />
            <ZoomOut className="cursor-pointer" />
          </div>
          <div className="w-1/2">
            <Progress
              progress={80}
              color="teal"
              theme={{ color: { teal: "bg-secondary" } }}
            />
          </div>
          <div className="flex items-center gap-2">
            <Expand className="cursor-pointer" />
            <CloudDownload className="cursor-pointer" />
          </div>
        </div>
      </footer>
    </div>
  );
}

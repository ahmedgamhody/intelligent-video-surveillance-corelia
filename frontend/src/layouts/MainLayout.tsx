import { ChannelsSideBar } from "../components/SideBar/ChannelsSideBar";
import { NavBar } from "../components/headers/NavBar";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { ChevronRight } from "lucide-react";
import { Tooltip } from "flowbite-react";
import { openChannelsSidebar, openPlotsSidebar } from "../store/ui/uiSlice";
import PlotsSideBar from "../components/SideBar/PlotsSideBar";
import { useState } from "react";
import { PlotsConditionsType } from "../types";
import HomePage from "../pages/homePage/HomePage";

export default function MainLayout() {
  const [plotsConditions, setPlotsConditions] = useState<PlotsConditionsType>({
    plots: true,
    sourceName: true,
    boxes: true,
    masks: true,
    classes: true,
    confidence: false,
    keypoints: true,
    timestamp: true,
    classesCount: true,
    framesRate: true,
    trackingIds: true,
    dateTime: true,
    classesSummations: 1,
    trackingLines: 1,
    heatMap: 1,
  });

  const { isChannelsSidebarOpen, isPlotsSidebarOpen } = useAppSelector(
    (state) => state.ui
  );
  const dispatch = useAppDispatch();
  return (
    <div className="bg-section h-screen flex flex-col">
      <NavBar />
      <div className="flex flex-1 w-full bg-gray-50 overflow-hidden">
        {/* Left Side - Channels */}
        {isChannelsSidebarOpen ? (
          <ChannelsSideBar />
        ) : (
          <div className="w-10 h-full pt-2 flex flex-col items-center justify-center">
            <Tooltip
              content="Open Channels Sidebar"
              placement="right"
              arrow={false}
            >
              <ChevronRight
                className="cursor-pointer text-secondary hover:text-primary duration-200"
                onClick={() => dispatch(openChannelsSidebar())}
                size={35}
              />
            </Tooltip>
          </div>
        )}

        {/* Main Content */}
        <div className="flex-1 bg-section flex flex-col min-h-0">
          <HomePage plotsConditions={plotsConditions} />
        </div>

        {/* Right Side - Plots */}
        {isPlotsSidebarOpen ? (
          <div className="w-72 h-full  flex flex-col items-center justify-center ">
            <PlotsSideBar
              plotsConditions={plotsConditions}
              setPlotsConditions={setPlotsConditions}
            />
          </div>
        ) : (
          <div className="w-10 h-full  flex flex-col items-center justify-center bg-section">
            <div className="w-10 h-full  flex flex-col items-center justify-center bg-white">
              <Tooltip
                content="Open Plots Sidebar"
                placement="left"
                arrow={false}
              >
                <ChevronRight
                  className="cursor-pointer text-secondary hover:text-primary duration-200 rotate-180"
                  onClick={() => dispatch(openPlotsSidebar())}
                  size={35}
                />
              </Tooltip>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

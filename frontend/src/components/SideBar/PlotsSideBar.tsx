import { CircleChevronRight, Settings } from "lucide-react";
import { ToggleSwitch, Tooltip } from "flowbite-react";
import { Sidebar } from "flowbite-react";
import { useAppDispatch } from "../../store/hooks";

import { closePlotsSidebar } from "../../store/ui/uiSlice";
import { PlotsConditionsProps, PlotsConditionsType } from "../../types";
import PlotToggle from "../../pages/Live streaming/Plots/PlotToggle";
const toggleItems: {
  label: string;
  name: keyof PlotsConditionsType;
  type: "boolean" | "number";
  space?: boolean;
}[] = [
  { label: "Source name", name: "sourceName", type: "boolean" },
  { label: "Date-Time", name: "dateTime", type: "boolean" },
  { label: "Frames rate", name: "framesRate", type: "boolean" },
  { label: "Classes Counts", name: "classesCount", type: "boolean" },
  {
    label: "Classes Summations",
    name: "classesSummations",
    type: "number",
    space: true,
  },
  { label: "Boxes", name: "boxes", type: "boolean" },
  { label: "Classes", name: "classes", type: "boolean" },
  { label: "Tracking IDs", name: "trackingIds", type: "boolean", space: true },
  { label: "Masks", name: "masks", type: "boolean" },
  { label: "Keypoints", name: "keypoints", type: "boolean", space: true },
  { label: "Confidence", name: "confidence", type: "boolean", space: true },
  { label: "Tracking Lines", name: "trackingLines", type: "number" },
  { label: "Heat Map", name: "heatMap", type: "number" },
];

export default function PlotsSideBar({
  plotsConditions,
  setPlotsConditions,
}: PlotsConditionsProps) {
  const dispatch = useAppDispatch();
  return (
    <Sidebar
      aria-label="Sidebar with content separator example"
      className="h-full bg-section w-full "
    >
      <Sidebar.Items className="h-5/6 flex justify-between flex-col">
        <Sidebar.ItemGroup>
          <div className="mb-5">
            <Tooltip content="Hide Sidebar">
              <CircleChevronRight
                className="text-secondary cursor-pointer"
                strokeWidth={2}
                onClick={() => {
                  dispatch(closePlotsSidebar());
                }}
              />
            </Tooltip>
          </div>
          <div className="bg-section p-2 rounded-md gap-3 flex flex-col h-full ">
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-bold tracking-wide">Plots</h1>
              <ToggleSwitch
                id={"plots"}
                checked={plotsConditions.plots}
                theme={{
                  toggle: {
                    checked: {
                      off: "bg-gray-400",
                      color: {
                        cyan: "bg-secondary",
                      },
                    },
                  },
                }}
                color="cyan"
                onChange={() =>
                  setPlotsConditions((prev) => ({
                    ...prev,
                    plots: !prev.plots,
                  }))
                }
              />
              <Settings className=" cursor-pointer" />
            </div>
            <div className="grid grid-cols-1 gap-2 flex-1">
              {toggleItems?.map((item) =>
                item.type === "boolean" ? (
                  <PlotToggle
                    key={item.name}
                    label={item.label}
                    name={item.name}
                    value={plotsConditions[item.name] as boolean}
                    plotsConditions={plotsConditions}
                    space={item.space}
                    onChange={(name) =>
                      setPlotsConditions((prev) => ({
                        ...prev,
                        [name]: !prev[name],
                      }))
                    }
                  />
                ) : (
                  <div key={item.name}>
                    <div
                      key={item.name}
                      className={`flex gap-1 items-center justify-between`}
                    >
                      <label className="text-sm font-medium">
                        {item.label}
                      </label>
                      <input
                        type="number"
                        min={0}
                        value={plotsConditions[item.name] as number}
                        disabled={!plotsConditions.plots}
                        placeholder="1"
                        onChange={(e) =>
                          setPlotsConditions((prev) => ({
                            ...prev,
                            [item.name]: Number(e.target.value),
                          }))
                        }
                        className={`border border-gray-300 rounded px-2 py-1 text-sm w-11
                        ${
                          plotsConditions.plots
                            ? "bg-white"
                            : "bg-gray-200 opacity-50 cursor-not-allowed"
                        }
                        `}
                      />
                    </div>
                    {item.space && <hr className="border-t border-gray-400" />}
                  </div>
                )
              )}
            </div>
          </div>
        </Sidebar.ItemGroup>
      </Sidebar.Items>
    </Sidebar>
  );
}

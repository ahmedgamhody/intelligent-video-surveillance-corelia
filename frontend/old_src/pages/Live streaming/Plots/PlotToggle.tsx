import { ToggleSwitch, Label } from "flowbite-react";
import { PlotsConditionsType } from "../../../types";

type PlotToggleProps = {
  label?: string;
  name: keyof PlotsConditionsType;
  value: boolean;
  onChange: (name: keyof PlotsConditionsType) => void;
  plotsConditions?: PlotsConditionsType;
  space?: boolean;
};

export default function PlotToggle({
  label,
  name,
  value,
  onChange,
  plotsConditions,
  space,
}: PlotToggleProps) {
  return (
    <>
      <div className={`flex items-center justify-between w-full`}>
        <Label className="tracking-wide" htmlFor={name} value={label} />
        <ToggleSwitch
          id={name}
          disabled={!plotsConditions?.plots}
          // checked={!plotsConditions?.plots ? false : value}
          checked={value}
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
          onChange={() => onChange(name)}
        />
      </div>
      {space && <hr className="border-t border-gray-400" />}
    </>
  );
}

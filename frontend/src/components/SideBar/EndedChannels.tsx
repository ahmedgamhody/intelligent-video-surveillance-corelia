import { RotateCcw, Trash2 } from "lucide-react";
import { useAppSelector } from "../../store/hooks";

export default function EndedChannels() {
  const { endedChannels } = useAppSelector((state) => state.channels);
  return (
    <div className="px-1">
      <h1 className="text-l font-bold mb-2 text-secondary">Ended</h1>
      <ul>
        {endedChannels?.map((channel, index) => (
          <li
            className="mb-2  p-2 rounded-lg flex justify-between items-center  cursor-pointer  hover:bg-gray-300 duration-150"
            key={index}
          >
            <p>{channel}</p>
            <div className="flex gap-2 ">
              <RotateCcw size={18} />
              <Trash2 size={18} />
            </div>
          </li>
        ))}
      </ul>
      {endedChannels?.length === 0 && (
        <p className="text-center">No Ended Channels</p>
      )}
    </div>
  );
}

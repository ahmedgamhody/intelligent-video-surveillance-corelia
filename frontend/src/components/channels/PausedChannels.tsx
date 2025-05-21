import { CirclePause, CirclePlay } from "lucide-react";
import { useAppSelector } from "../../store/hooks";

export default function PausedChannels() {
  const { pausedChannels } = useAppSelector((state) => state.channels);
  return (
    <div className="px-1">
      <h1 className="text-l font-bold mb-2 text-secondary">Paused</h1>
      <ul>
        {pausedChannels?.map((channel, index) => (
          <li
            className="mb-2  p-2 rounded-lg flex justify-between items-center  cursor-pointer  hover:bg-gray-300 duration-150"
            key={index}
          >
            <p>{channel}</p>
            <div className="flex gap-2 ">
              <CirclePlay size={18} />
              <CirclePause size={18} />
            </div>
          </li>
        ))}
      </ul>
      {pausedChannels?.length === 0 && (
        <p className="text-center">No Paused Channels</p>
      )}
    </div>
  );
}

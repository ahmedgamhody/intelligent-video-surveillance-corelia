import { FilePenLine, RotateCcw } from "lucide-react";
import { useAppSelector } from "../../store/hooks";
// import { useAppDispatch } from "../../store/hooks";

// import { restoreChannelFromEnded } from "../../store/channel/channelSlice";
import RemoveIconAction from "../actions/RemoveIconAction";
export default function EndedChannels() {
  const { endedChannels } = useAppSelector((state) => state.channels);
  // const dispatch = useAppDispatch();

  // const handleRestoreChannel = async (channel: string) => {
  //   dispatch(restoreChannelFromEnded(channel));
  // };
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
              <FilePenLine size={18} />
              <RotateCcw
                size={18}
                // onClick={() => {
                //   handleRestoreChannel(channel);
                // }}
              />
              <RemoveIconAction channel={channel} />
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

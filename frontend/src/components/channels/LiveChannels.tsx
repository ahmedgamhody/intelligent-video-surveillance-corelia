import { CirclePause, FilePenLine } from "lucide-react";
import { useAppDispatch, useAppSelector } from "../../store/hooks";
import {
  addChannelToPaused,
  setSelectedChannel,
} from "../../store/channel/channelSlice";
import MoveToEndSectionIconAction from "../actions/MoveToEndSectionIconAction";
import Swal from "sweetalert2";
import { pauseChannel } from "../../utils/api";

export default function LiveChannels() {
  const { LiveChannels, selectedChannel } = useAppSelector(
    (state) => state.channels
  );
  const dispatch = useAppDispatch();
  const handlePauseChannel = async (channel: string) => {
    Swal.fire({
      title: "Do you want to Pause this Channel?",
      icon: "question",
      showCancelButton: true,
      confirmButtonColor: "#49CC95",
      cancelButtonColor: "#d33",
      confirmButtonText: "Yes, pause it!",
    }).then(async (result) => {
      if (result.isConfirmed) {
        try {
          await pauseChannel(channel);

          if (selectedChannel === channel) {
            dispatch(setSelectedChannel(""));
          }

          dispatch(addChannelToPaused(channel));
          Swal.fire({
            title: "Paused!",
            text: "Your Channel has been paused.",
            icon: "success",
          });
        } catch (error) {
          console.error("Error pausing channel:", error);
          Swal.fire({
            title: "Error!",
            text: "Failed to pause the Channel. Please try again.",
            icon: "error",
          });
        }
      }
    });
  };

  return (
    <div className="px-1">
      <h1 className="text-l font-bold mb-2 text-secondary">Live</h1>
      <ul>
        {LiveChannels?.map((channel, index) => (
          <li
            className="mb-2  p-2 rounded-lg flex justify-between items-center  cursor-pointer  hover:bg-gray-300 duration-150"
            key={index}
            onClick={() => {
              dispatch(setSelectedChannel(channel));
            }}
          >
            <p>{channel}</p>
            <div className="flex gap-2 ">
              <FilePenLine size={18} />
              <CirclePause
                size={18}
                onClick={() => handlePauseChannel(channel)}
              />
              <MoveToEndSectionIconAction channel={channel} />
            </div>
          </li>
        ))}
      </ul>

      {LiveChannels?.length === 0 && (
        <p className="text-center">No Live Channels</p>
      )}
    </div>
  );
}

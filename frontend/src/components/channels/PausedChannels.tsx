import { CirclePlay, FilePenLine } from "lucide-react";
import { useAppDispatch, useAppSelector } from "../../store/hooks";
import { addChannel } from "../../store/channel/channelSlice";
import MoveToEndSectionIconAction from "../actions/MoveToEndSectionIconAction";
import Swal from "sweetalert2";
import { resumeChannel } from "../../utils/api";

export default function PausedChannels() {
  const { pausedChannels } = useAppSelector((state) => state.channels);
  const dispatch = useAppDispatch();
  const handlePlayChannel = async (channel: string) => {
    Swal.fire({
      title: "Do you want to Resume this Channel?",
      icon: "question",
      showCancelButton: true,
      confirmButtonColor: "#49CC95",
      cancelButtonColor: "#d33",
      confirmButtonText: "Yes, resume it!",
    }).then(async (result) => {
      if (result.isConfirmed) {
        try {
          await resumeChannel(channel);
          dispatch(addChannel(channel));

          Swal.fire({
            title: "Resumed!",
            text: "Your Channel has been resumed.",
            icon: "success",
          });
        } catch (error) {
          console.error("Error resuming channel:", error);
          Swal.fire({
            title: "Error!",
            text: "Failed to resume the Channel. Please try again.",
            icon: "error",
          });
        }
      }
    });
  };

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
              <FilePenLine size={18} />
              <CirclePlay
                size={18}
                onClick={() => handlePlayChannel(channel)}
              />
              <MoveToEndSectionIconAction channel={channel} />
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

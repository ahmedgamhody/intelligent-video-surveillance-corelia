import { Eraser } from "lucide-react";
import { useAppDispatch, useAppSelector } from "../../store/hooks";
import {
  addChannelToEnded,
  setSelectedChannel,
} from "../../store/channel/channelSlice";
import Swal from "sweetalert2";
import { endChannel } from "../../utils/api";

export default function MoveToEndSectionIconAction({
  channel,
}: {
  channel: string;
}) {
  const dispatch = useAppDispatch();
  const { selectedChannel } = useAppSelector((state) => state.channels);
  const handleMoveChannelToEnd = async (channel: string) => {
    Swal.fire({
      title: "Do you want to move this Channel to the end?",
      icon: "question",
      showCancelButton: true,
      confirmButtonColor: "#49CC95",
      cancelButtonColor: "#d33",
      confirmButtonText: "Yes, move it!",
    }).then(async (result) => {
      if (result.isConfirmed) {
        try {
          await endChannel(channel);

          if (selectedChannel === channel) {
            dispatch(setSelectedChannel(""));
          }

          dispatch(addChannelToEnded(channel));
          Swal.fire({
            title: "Moved!",
            text: "Your Channel has been moved to the end.",
            icon: "success",
          });
        } catch (error) {
          console.error("Error moving channel:", error);
          Swal.fire({
            title: "Error!",
            text: "Failed to move the Channel. Please try again.",
            icon: "error",
          });
        }
      }
    });
  };
  return <Eraser size={18} onClick={() => handleMoveChannelToEnd(channel)} />;
}

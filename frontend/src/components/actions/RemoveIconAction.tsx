import { Trash2 } from "lucide-react";
import Swal from "sweetalert2";
import {
  removeChannel,
  setSelectedChannel,
} from "../../store/channel/channelSlice";
import { useAppDispatch, useAppSelector } from "../../store/hooks";

export default function RemoveIconAction({ channel }: { channel: string }) {
  const dispatch = useAppDispatch();
  const { selectedChannel } = useAppSelector((state) => state.channels);
  const handleRemoveChannel = async (channel: string) => {
    Swal.fire({
      title: "Do you want to delete this Channel?",
      text: "You won't be able to revert this!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Yes, delete it!",
    }).then(async (result) => {
      if (result.isConfirmed) {
        try {
          if (selectedChannel === channel) {
            dispatch(setSelectedChannel(""));
          }

          dispatch(removeChannel(channel));
          Swal.fire({
            title: "Deleted!",
            text: "Your Channel has been deleted.",
            icon: "success",
          });
        } catch (error) {
          console.error("Error deleting channel:", error);
          Swal.fire({
            title: "Error!",
            text: "Failed to delete the Channel. Please try again.",
            icon: "error",
          });
        }
      }
    });
  };
  return (
    <Trash2
      size={18}
      onClick={() => {
        handleRemoveChannel(channel);
      }}
    />
  );
}

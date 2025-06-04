import { CircleChevronLeft, CirclePlus } from "lucide-react";
import { Tooltip } from "flowbite-react";
import { Sidebar } from "flowbite-react";
import { useState } from "react";
import { useAppDispatch } from "../../store/hooks";
import AddChannelModal from "../Modal/AddChannelModal";
import { closeChannelsSidebar } from "../../store/ui/uiSlice";
import LiveChannels from "../channels/LiveChannels";
import PausedChannels from "../channels/PausedChannels";
import EndedChannels from "./EndedChannels";

export function ChannelsSideBar() {
  const [openModal, setOpenModal] = useState(false);

  const dispatch = useAppDispatch();

  return (
    <Sidebar
      aria-label="Sidebar with content separator example"
      className=" bg-section "
    >
      <Sidebar.Items className="flex justify-between flex-col ">
        <Sidebar.ItemGroup>
          <div className="mb-4 flex justify-end">
            <Tooltip content="Hide Sidebar">
              <CircleChevronLeft
                className="text-secondary cursor-pointer"
                strokeWidth={2}
                onClick={() => {
                  dispatch(closeChannelsSidebar());
                }}
              />
            </Tooltip>
          </div>
          <div
            className=" flex items-center  justify-evenly "
            style={{
              marginBottom: "25px",
            }}
          >
            <h1 className="text-xl font-bold ">Channels </h1>
            <Tooltip content="Add Channel">
              <CirclePlus
                strokeWidth={3}
                className="text-secondary cursor-pointer"
                onClick={() => setOpenModal(true)}
              />
            </Tooltip>
          </div>

          <div className="flex flex-col gap-4 ">
            <LiveChannels />
            <hr className="border-t border-gray-400" />
            <PausedChannels />
            <hr className="border-t border-gray-400" />
            <EndedChannels />
          </div>

          {/* Add Channel Modal */}
          <AddChannelModal openModal={openModal} setOpenModal={setOpenModal} />
        </Sidebar.ItemGroup>
      </Sidebar.Items>
    </Sidebar>
  );
}

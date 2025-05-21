import { CirclePause, FilePenLine } from "lucide-react";
import { useAppSelector } from "../../store/hooks";
// import {
//   Accordion,
//   AccordionContent,
//   AccordionPanel,
//   AccordionTitle,
// } from "flowbite-react";

export default function LiveChannels() {
  const { LiveChannels } = useAppSelector((state) => state.channels);

  return (
    <div className="px-1">
      <h1 className="text-l font-bold mb-2 text-secondary">Live</h1>
      <ul>
        {LiveChannels?.map((channel, index) => (
          <li
            className="mb-2  p-2 rounded-lg flex justify-between items-center  cursor-pointer  hover:bg-gray-300 duration-150"
            key={index}
            // onClick={() => {
            //   dispatch(setSelectedChannel(channel));
            //   dispatch(setIsPlayingTrue());
            //   nav("/video-archive");
            // }}
          >
            <p>{channel}</p>
            <div className="flex gap-2 ">
              <CirclePause size={18} />
              <FilePenLine size={18} />
            </div>
          </li>
        ))}
      </ul>
      {/* <Accordion
        theme={{
          title: {
            arrow: {
              base: "p-1",
            },
            base: "flex w-full items-center justify-between p-5 text-left font-medium text-gray-500 first:rounded-t-lg last:rounded-b-lg dark:text-gray-400",
          },
          content: {
            base: "p-2",
          },
        }}
      >
        <AccordionPanel>
          <AccordionTitle className="text-l font-bold mb-2 text-secondary">
            Live
          </AccordionTitle>
          <AccordionContent>
            <ul>
              {LiveChannels?.map((channel, index) => (
                <li
                  className="mb-2 bg-gray-200 p-2 rounded-lg flex justify-between items-center  cursor-pointer  hover:bg-gray-300 duration-150"
                  key={index}
                  // onClick={() => {
                  //   dispatch(setSelectedChannel(channel));
                  //   dispatch(setIsPlayingTrue());
                  //   nav("/video-archive");
                  // }}
                >
                  <p>{channel}</p>
                  <div className="flex gap-2 ">
                    <CirclePause size={18} />
                    <FilePenLine size={18} />
                  </div>
                </li>
              ))}
            </ul>
          </AccordionContent>
        </AccordionPanel>
      </Accordion> */}
      {LiveChannels?.length === 0 && (
        <p className="text-center">No Live Channels</p>
      )}
    </div>
  );
}

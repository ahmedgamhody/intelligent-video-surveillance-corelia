import { IVideoStreamProps } from "../../interfaces";
import VideoSkeleton from "../../ui/skeletons/VideoSkeleton";
export default function VideoStream({ imageSrcs, stream }: IVideoStreamProps) {
  const { name } = stream;
  const badges = ["People", "Bag", "Suspicious item", "Car", "Smoke"];
  const badgesRender = badges.map((b) => (
    <span
      key={b}
      className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-blue-700/10 ring-inset"
    >
      {b}
    </span>
  ));
  return (
    <div className="flex flex-col lg:flex-row  bg-white  p-5  justify-evenly rounded-lg">
      <div>
        {imageSrcs.length ? (
          imageSrcs.map((image, index) => {
            return (
              <img
                key={index}
                src={`data:image/jpeg;base64,${image}`}
                alt="Streamed from FastAPI"
              />
            );
          })
        ) : (
          <VideoSkeleton />
        )}
      </div>

      <div className="bg-section p-7 w-full lg:w-1/3 flex flex-col gap-6 rounded -lg">
        {/* Show Objects */}
        <div className="space-y-2">
          <h3 className="text-secondary font-bold">{name}</h3>
          <div className="flex flex-wrap gap-2">{badgesRender}</div>
        </div>

        {/* Accidents */}
        <div className="space-y-2">
          <h3 className="text-secondary font-bold">Accidents</h3>
          <div className="flex justify-between">
            <p className="text-text">Crowd</p>
            <p className="text-blue-700 underline">8:46:34</p>
          </div>
          <div className="flex justify-between">
            <p className="text-text">Bag indoors</p>
            <p className="text-blue-700 underline">21:58:12</p>
          </div>
        </div>

        {/* Video Details */}
        <div className="space-y-2">
          <h3 className="text-secondary font-bold">Video details</h3>
          <div className="flex justify-between">
            <p className="text-text">Length</p>
            <p className="!text-[#ADADAD]">24:00:00</p>
          </div>
          <div className="flex justify-between">
            <p className="text-text">Size</p>
            <p className="!text-[#ADADAD]">12.5Mb</p>
          </div>
          <div className="flex justify-between">
            <p className="text-text">Created</p>
            <p className="!text-[#ADADAD]">20-06-2023</p>
          </div>
          <div className="flex justify-between">
            <p className="text-text">Camera #</p>
            <p className="!text-[#ADADAD]">128</p>
          </div>
        </div>
      </div>
    </div>
  );
}

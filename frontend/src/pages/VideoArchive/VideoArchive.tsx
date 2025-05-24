import { useEffect, useRef, useState } from "react";
import { useAppSelector } from "../../store/hooks";
import VideoStream from "./VideoStream";
import axios from "axios";
const apiUrl = import.meta.env.VITE_API_URL_SOCKET;

export default function VideoArchive() {
  const [jsonData, setJsonData] = useState([]);
  console.log(jsonData);
  const { selectedChannel, channelsList } = useAppSelector(
    (state) => state.channels
  );
  const [imageSrcs, setImageSrcs] = useState([]);

  const socketRef = useRef<WebSocket | null>(null);
  useEffect(() => {
    if (!selectedChannel) return;

    console.log("Selected Channel:", selectedChannel);

    if (socketRef.current) {
      socketRef.current.close();
    }
    const socket = new WebSocket(`${apiUrl}?channel_name=${selectedChannel}`);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("WebSocket connected:", selectedChannel);
    };

    socket.onmessage = (event) => {
      const res = JSON.parse(event.data);
      const images = res.frames_results || [];
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const filteredImages = images.filter((image: any) => image !== null);
      setImageSrcs(filteredImages);
      console.log("filteredImages", filteredImages);
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    socket.onclose = () => {
      console.log("WebSocket closed:", selectedChannel);
    };

    return () => {
      if (socketRef.current === socket) {
        console.log("Cleanup: Closing WebSocket...");
        socket.close();
        socketRef.current = null;
      }
    };
  }, [selectedChannel]);
  // useEffect(() => {
  //   if (!selectedChannel) return;
  //   console.log("Selected Channel:", selectedChannel);
  //   let socket: WebSocket | null = null;
  //   if (selectedChannel) {
  //     socket = new WebSocket(
  //       `ws://10.100.102.6:3333/ivs/v4/streamer/ws?name=${selectedChannel}`
  //     );

  //     socket.onmessage = (event) => {
  //       const res = JSON.parse(event.data);
  //       const images = res.frames_results;
  //       //set only image has a src not null
  //       // eslint-disable-next-line @typescript-eslint/no-explicit-any
  //       const filteredImages = images.filter((image: any) => image !== null);
  //       setImageSrcs(filteredImages);
  //       console.log("filteredImages", filteredImages);
  //     };

  //     socket.onclose = () => {
  //       console.log("WebSocket closed");
  //     };
  //   }

  //   return () => {
  //     if (socket) {
  //       socket.close();
  //     }
  //   };
  // }, [selectedChannel]);

  useEffect(() => {
    if (channelsList?.length === 0) {
      console.log(
        "All channels deleted, clearing images and closing WebSocket."
      );
      setImageSrcs([]);
    }
  }, [channelsList]);

  /// test data and websocket by json server and static images and data
  useEffect(() => {
    async function getData() {
      const res = await axios("http://localhost:3000/data");
      const data = res.data;
      setJsonData(data);
    }
    getData();
  }, []);
  return (
    <div className="flex flex-col gap-5 lg:gap-8 p-5 lg:p-8 bg-section">
      {jsonData?.map((data, index) => (
        <VideoStream key={index} imageSrcs={imageSrcs} stream={data} />
      ))}
      {jsonData?.length === 0 && (
        <div className="flex justify-center items-center h-full w-full">
          <p className="text-2xl">No data available</p>{" "}
        </div>
      )}
    </div>
  );
}

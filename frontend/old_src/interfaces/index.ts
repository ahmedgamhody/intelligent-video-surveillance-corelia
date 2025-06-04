interface IFrameData {
  source_name: string;
  frame: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  boxes: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  masks: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  keypoints: any[];
  frame_rate: string;
}
interface IWSResponse {
  timestamp: string;
  data: IFrameData[];
}

interface TSources {
  source_name: string;
  source: string | File;
  type: "url" | "file";
  file?: File;
}
export type { IFrameData, TSources, IWSResponse };

export type TLoading = "idle" | "pending" | "succeeded" | "failed";
export type FieldType = {
  name?: string;
  confidence: number;
  overlapping: number;
  augment: boolean;
  realTimeMode: boolean;
  tracking: boolean;
  withReId: boolean;
};

export type TModalType = {
  name: string;
  task: string;
  weight: string;
};

export type PlotsConditionsType = {
  plots: boolean;
  sourceName: boolean;
  boxes: boolean;
  masks: boolean;
  classes: boolean;
  confidence: boolean;
  keypoints: boolean;
  timestamp: boolean;
  classesCount: boolean;
  framesRate: boolean;
  trackingIds: boolean;
  dateTime: boolean;
  classesSummations: number | boolean;
  trackingLines: number | boolean;
  heatMap: number | boolean;
};

export type PlotsConditionsProps = {
  plotsConditions: PlotsConditionsType;
  setPlotsConditions: React.Dispatch<React.SetStateAction<PlotsConditionsType>>;
};

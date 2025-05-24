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
  dateTime: boolean;
  framesRate: boolean;
  
  classesCount: boolean;
  classesSummations: boolean;

  classes: boolean;
  trackingIds: boolean;
  objectsDurations: boolean;

  boxes: boolean;
  masks: boolean;
  keypoints: boolean;

  confidence: boolean;

  // timestamp: boolean;
  trackingLines: boolean;
  heatMap: boolean;
  blur: boolean;
};

export type PlotsConditionsProps = {
  plotsConditions: PlotsConditionsType;
  setPlotsConditions: React.Dispatch<React.SetStateAction<PlotsConditionsType>>;
};

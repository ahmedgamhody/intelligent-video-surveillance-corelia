import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import Cookies from "js-cookie";

const savedChannels = Cookies.get("LiveChannels");
// const savedPausedChannels = Cookies.get("pausedChannels");

type InitialStateType = {
  LiveChannels: string[];
  pausedChannels: string[];
  endedChannels: string[];
  selectedChannel: string | undefined;
  isPlaying: boolean;
};

const initialState: InitialStateType = {
  // LiveChannels: savedChannels
  //   ? JSON.parse(savedChannels)
  //   : ["Channel 1", "Channel 2", "Channel 3"],
  // pausedChannels: ["Channel 1", "Channel 2", "Channel 3"],
  // endedChannels: ["Channel 1", "Channel 2", "Channel 3"],
  LiveChannels: savedChannels ? JSON.parse(savedChannels) : [],
  pausedChannels: [],
  endedChannels: [],
  selectedChannel: undefined,
  isPlaying: false,
};

const channelsSlice = createSlice({
  name: "channels",
  initialState,
  reducers: {
    addChannel: (state, action: PayloadAction<string>) => {
      if (!state.LiveChannels.includes(action.payload)) {
        state.LiveChannels.push(action.payload);
      }
      Cookies.set("LiveChannels", JSON.stringify(state.LiveChannels));
    },
    setSelectedChannel: (state, action: PayloadAction<string>) => {
      state.selectedChannel = action.payload;
    },
    setIsPlayingTrue: (state) => {
      state.isPlaying = true;
    },
    swapIsPlaying: (state) => {
      state.isPlaying = !state.isPlaying;
    },
    clearChannels: (state) => {
      state.LiveChannels = [];
      Cookies.remove("LiveChannels");
      state.selectedChannel = undefined;
      state.isPlaying = false;
    },
  },
});

export const {
  addChannel,
  clearChannels,
  setSelectedChannel,
  setIsPlayingTrue,
  swapIsPlaying,
} = channelsSlice.actions;
export default channelsSlice.reducer;

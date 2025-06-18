import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import Cookies from "js-cookie";

const savedLiveChannels = Cookies.get("liveChannels");
const savedPausedChannels = Cookies.get("pausedChannels");
const savedEndedChannels = Cookies.get("endedChannels");

type InitialStateType = {
  LiveChannels: string[];
  pausedChannels: string[];
  endedChannels: string[];
  selectedChannel: string | undefined;
};

const initialState: InitialStateType = {
  LiveChannels: savedLiveChannels ? JSON.parse(savedLiveChannels) : [],
  pausedChannels: savedPausedChannels ? JSON.parse(savedPausedChannels) : [],
  endedChannels: savedEndedChannels ? JSON.parse(savedEndedChannels) : [],
  selectedChannel: undefined,
};

const channelsSlice = createSlice({
  name: "channels",
  initialState,
  reducers: {
    addChannel: (state, action: PayloadAction<string>) => {
      // إضافة قناة جديدة إلى LiveChannels فقط إذا لم تكن موجودة
      if (!state.LiveChannels.includes(action.payload)) {
        // إزالة القناة من جميع الأقسام الأخرى
        state.pausedChannels = state.pausedChannels.filter(
          (channel) => channel !== action.payload
        );
        state.endedChannels = state.endedChannels.filter(
          (channel) => channel !== action.payload
        );
        state.LiveChannels.push(action.payload);
      }
      Cookies.set("liveChannels", JSON.stringify(state.LiveChannels));
      Cookies.set("pausedChannels", JSON.stringify(state.pausedChannels));
      Cookies.set("endedChannels", JSON.stringify(state.endedChannels));
    },
    setSelectedChannel: (state, action: PayloadAction<string>) => {
      state.selectedChannel = action.payload;
    },

    clearChannels: (state) => {
      state.LiveChannels = [];
      Cookies.remove("liveChannels");
      state.selectedChannel = undefined;
    },

    // نقل قناة من Live إلى Paused
    addChannelToPaused: (state, action: PayloadAction<string>) => {
      if (!state.pausedChannels.includes(action.payload)) {
        // إزالة القناة من LiveChannels
        state.LiveChannels = state.LiveChannels.filter(
          (channel) => channel !== action.payload
        );
        // إضافة القناة إلى PausedChannels
        state.pausedChannels.push(action.payload);
      }
      Cookies.set("liveChannels", JSON.stringify(state.LiveChannels));
      Cookies.set("pausedChannels", JSON.stringify(state.pausedChannels));
    },

    // نقل قناة من Paused إلى Ended
    addChannelToEnded: (state, action: PayloadAction<string>) => {
      if (!state.endedChannels.includes(action.payload)) {
        // إزالة القناة من PausedChannels
        state.pausedChannels = state.pausedChannels.filter(
          (channel) => channel !== action.payload
        );
        state.LiveChannels = state.LiveChannels.filter(
          (channel) => channel !== action.payload
        );
        // إضافة القناة إلى EndedChannels
        state.endedChannels.push(action.payload);
      }
      Cookies.set("pausedChannels", JSON.stringify(state.pausedChannels));
      Cookies.set("endedChannels", JSON.stringify(state.endedChannels));
      Cookies.set("liveChannels", JSON.stringify(state.LiveChannels));
    }, // حذف قناة نهائياً من EndedChannels
    removeChannel: (state, action: PayloadAction<string>) => {
      // حذف القناة من جميع الأقسام نهائياً
      state.endedChannels = state.endedChannels.filter(
        (channel) => channel !== action.payload
      );
      state.LiveChannels = state.LiveChannels.filter(
        (channel) => channel !== action.payload
      );
      state.pausedChannels = state.pausedChannels.filter(
        (channel) => channel !== action.payload
      );
      Cookies.set("endedChannels", JSON.stringify(state.endedChannels));
      Cookies.set("liveChannels", JSON.stringify(state.LiveChannels));
      Cookies.set("pausedChannels", JSON.stringify(state.pausedChannels));
    },

    // استعادة قناة من Ended (يمكن إضافة الوظيفة لاحقاً)
    restoreChannelFromEnded: (state, action: PayloadAction<string>) => {
      // إزالة القناة من EndedChannels
      state.endedChannels = state.endedChannels.filter(
        (channel) => channel !== action.payload
      );
      // إضافة القناة إلى PausedChannels (أو يمكن إضافتها مباشرة إلى Live حسب المطلوب)
      if (!state.pausedChannels.includes(action.payload)) {
        state.pausedChannels.push(action.payload);
      }
      Cookies.set("endedChannels", JSON.stringify(state.endedChannels));
      Cookies.set("pausedChannels", JSON.stringify(state.pausedChannels));
    },
  },
});

export const {
  addChannel,
  clearChannels,
  setSelectedChannel,
  addChannelToPaused,
  addChannelToEnded,
  removeChannel,
  restoreChannelFromEnded,
} = channelsSlice.actions;
export default channelsSlice.reducer;

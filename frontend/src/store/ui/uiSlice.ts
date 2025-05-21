import { createSlice } from "@reduxjs/toolkit";

type InitialStateType = {
  isChannelsSidebarOpen: boolean;
  isPlotsSidebarOpen: boolean;
  // Add other UI-related state properties here as needed
};

const initialState: InitialStateType = {
  isChannelsSidebarOpen: true,
  isPlotsSidebarOpen: false,
  // Initialize other UI-related state properties here
};

const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    openChannelsSidebar: (state) => {
      state.isChannelsSidebarOpen = true;
    },
    closeChannelsSidebar: (state) => {
      state.isChannelsSidebarOpen = false;
    },
    openPlotsSidebar: (state) => {
      state.isPlotsSidebarOpen = true;
    },
    closePlotsSidebar: (state) => {
      state.isPlotsSidebarOpen = false;
    },
  },
});

export const {
  openChannelsSidebar,
  closeChannelsSidebar,
  openPlotsSidebar,
  closePlotsSidebar,
} = uiSlice.actions;
export default uiSlice.reducer;

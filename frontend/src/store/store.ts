import { configureStore } from "@reduxjs/toolkit";
import auth from "./auth/authSlice";
import channels from "./channel/channelSlice";
import ui from "./ui/uiSlice";
export const store = configureStore({
  reducer: {
    auth,
    channels,
    ui,
  },
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
// Inferred type: {posts: PostsState, comments: CommentsState, users: UsersState}
export type AppDispatch = typeof store.dispatch;

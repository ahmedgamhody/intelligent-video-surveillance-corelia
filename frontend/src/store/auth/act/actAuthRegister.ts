import { createAsyncThunk } from "@reduxjs/toolkit";

import axios from "axios";
import axiosErrorHandler from "../../../utils/axiosErrorHandler";
const BASE_URL = "http://localhost:8000";
type formData = {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  userRole: string;
};
const actAuthRegister = createAsyncThunk(
  "auth/actAuthRegister",
  async (formData: formData, thunk) => {
    const { rejectWithValue } = thunk;
    try {
      const res = await axios.post(`${BASE_URL}/user/register`, formData);
      return res.data;
    } catch (error) {
      return rejectWithValue(axiosErrorHandler(error));
    }
  }
);

export default actAuthRegister;

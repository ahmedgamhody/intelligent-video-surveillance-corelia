// make a axios instance with base url and interceptors
import axios from "axios";

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_URL_FOR_CHANNELS,
});

export default axiosInstance;

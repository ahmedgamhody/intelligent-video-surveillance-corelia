import { isAxiosError } from "axios";
export default function axiosErrorHandler(error: unknown) {
  if (isAxiosError(error)) {
    return (
      error.response?.data || error.message || error.response?.data.message
    );
  } else {
    return "Something went wrong";
  }
}

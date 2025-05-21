import { Route, Routes } from "react-router";
import MainLayout from "./layouts/MainLayout";
import HomePage from "./pages/homePage/HomePage";
import LoginPage from "./pages/loginPage/LoginPage";
import VideoArchive from "./pages/VideoArchive/VideoArchive";
import LiveStreaming from "./pages/Live streaming/LiveStreaming";
import DashboardPage from "./pages/Dashboard/DashboardPage";

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<MainLayout />}>
          <Route index element={<HomePage />} />
          <Route path="/video-archive" element={<VideoArchive />} />
          <Route path="/live-stream" element={<LiveStreaming />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Route>
      </Routes>
    </div>
  );
}

export default App;

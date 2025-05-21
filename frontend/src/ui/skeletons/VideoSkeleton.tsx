import ContentLoader from "react-content-loader";

const VideoSkeleton = () => (
  <ContentLoader
    speed={2}
    width={400}
    height={400}
    viewBox="0 0 500 500"
    backgroundColor="#f3f3f3"
    foregroundColor="#ecebeb"
  >
    <rect x="0" y="0" rx="15" ry="15" width="500" height="500" />
  </ContentLoader>
);

export default VideoSkeleton;

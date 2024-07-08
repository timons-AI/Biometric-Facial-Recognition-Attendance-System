import React, { useRef, useEffect } from "react";

const VideoFeed: React.FC = () => {
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const img = imgRef.current;
    if (img) {
      img.src = "http://localhost:5000/api/video_feed";
    }
  }, []);

  return (
    <div>
      <h2>Attendance System Video Feed</h2>
      <img
        ref={imgRef}
        alt="Video feed"
        style={{ maxWidth: "100%", height: "auto" }}
      />
    </div>
  );
};

export default VideoFeed;

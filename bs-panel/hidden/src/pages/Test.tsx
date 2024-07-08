import React, { useRef, useState } from "react";
import axios from "axios";
import { Button } from "@blueprintjs/core";

const AttendanceCapture: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [name, setName] = useState("");

  const startCamera = () => {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      })
      .catch((err) => console.error("Error accessing camera: ", err));
  };

  const captureImage = () => {
    const canvas = document.createElement("canvas");
    if (videoRef.current) {
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      canvas.getContext("2d")?.drawImage(videoRef.current, 0, 0);
      canvas.toBlob((blob) => {
        if (blob) {
          const formData = new FormData();
          formData.append("image", blob, "capture.jpg");
          axios
            .post("/recognize", formData)
            .then((response) => setName(response.data.name))
            .catch((error) => console.error("Recognition error: ", error));
        }
      });
    }
  };

  return (
    <div>
      <video ref={videoRef} autoPlay />
      <Button onClick={startCamera}>Start Camera</Button>
      <Button onClick={captureImage}>Capture</Button>
      {name && <p>Recognized: {name}</p>}
    </div>
  );
};

export default AttendanceCapture;

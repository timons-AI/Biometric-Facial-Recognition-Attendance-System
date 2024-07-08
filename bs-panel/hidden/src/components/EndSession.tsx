import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";
import axios from "axios";
import { Card, Button } from "@blueprintjs/core";
import { useParams, useNavigate } from "react-router-dom";

const EndSession: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const webcamRef = useRef<Webcam>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const navigate = useNavigate();

  const CAPTURE_INTERVAL = 1000; // Capture interval in milliseconds

  useEffect(() => {
    const captureInterval = setInterval(() => {
      if (!isProcessing) {
        capture();
      }
    }, CAPTURE_INTERVAL);

    return () => clearInterval(captureInterval);
  }, [isProcessing]);

  const capture = async () => {
    setIsProcessing(true);
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      await sendImageToBackend(imageSrc);
    }
    setIsProcessing(false);
  };

  const sendImageToBackend = async (imageSrc: string) => {
    try {
      const response = await axios.post(
        `http://localhost:5000/api/end-session/${sessionId}`,
        { image: imageSrc },
        { headers: { "Content-Type": "application/json" } }
      );

      if (response.data.success) {
        console.log("Session ended successfully");
        navigate("/"); // Redirect to home page after ending session
      }
    } catch (error) {
      console.error("Error ending session:", error);
    }
  };

  return (
    <div className="end-session p-4">
      <Card className="mb-4">
        <h2>End Session</h2>
        <p>Please look at the camera to end the session.</p>
        <div className="relative" style={{ height: "480px" }}>
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            videoConstraints={{
              width: 640,
              height: 480,
              facingMode: "user",
            }}
            className="w-full h-full object-cover"
          />
        </div>
        <Button onClick={() => navigate("/")} intent="primary" className="mt-2">
          Cancel
        </Button>
      </Card>
    </div>
  );
};

export default EndSession;

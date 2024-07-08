import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";
import axios from "axios";
import {
  Card,
  Button,
  ProgressBar,
  Dialog,
  InputGroup,
  FormGroup,
} from "@blueprintjs/core";
import { Intent } from "@blueprintjs/core";
import { useNavigate } from "react-router-dom";

interface RecognitionResult {
  matched: boolean;
  student_id?: string;
  name?: string;
  image_filename?: string;
  message?: string;
  qr_code?: string;
}

const FaceRecognition: React.FC = () => {
  const webcamRef = useRef<Webcam>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentImage, setCurrentImage] = useState<string | null>(null);
  const [imageStack, setImageStack] = useState<string[]>([]);
  const [isVideoActive, setIsVideoActive] = useState(true);
  const [countdown, setCountdown] = useState(5);
  const [recognizedUser, setRecognizedUser] =
    useState<RecognitionResult | null>(null);
  const [isQRDialogOpen, setIsQRDialogOpen] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  // Configuration variables
  const CAPTURE_INTERVAL = 1000; // Capture interval in milliseconds
  const RECOGNITION_DURATION = 30000; // Duration to show recognition result in milliseconds

  useEffect(() => {
    let captureInterval: NodeJS.Timeout;

    if (isVideoActive && !recognizedUser) {
      captureInterval = setInterval(() => {
        if (!isProcessing) {
          capture();
        }
      }, CAPTURE_INTERVAL);
    }

    return () => clearInterval(captureInterval);
  }, [isVideoActive, isProcessing, recognizedUser]);

  useEffect(() => {
    let recognitionTimer: NodeJS.Timeout;

    if (recognizedUser) {
      recognitionTimer = setTimeout(() => {
        handleReactivateVideo();
      }, RECOGNITION_DURATION);
    }

    return () => clearTimeout(recognitionTimer);
  }, [recognizedUser]);

  const capture = async () => {
    setIsProcessing(true);
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      await sendImageToBackend(imageSrc);
    }
    setIsProcessing(false);
  };

  const handleQRCodeScan = (qrCode: string) => {
    const sessionId = qrCode.split("/").pop();
    navigate(`/end-session/${sessionId}`);
  };

  const sendImageToBackend = async (imageSrc: string) => {
    try {
      const response = await axios.post<RecognitionResult>(
        "http://localhost:5000/api/live-recognition",
        { image: imageSrc },
        { headers: { "Content-Type": "application/json" } }
      );

      if (response.data.matched && response.data.image_filename) {
        setCurrentImage(
          `http://localhost:5000/temp_image/${response.data.image_filename}`
        );
        setIsVideoActive(false);
        setRecognizedUser(response.data);

        if (response.data.qr_code) {
          setIsQRDialogOpen(true);
          console.log("New session started. Scan QR code to end session.");
        } else {
          console.log("Student Recognized. Session already active");
        }
      }
    } catch (error) {
      console.error("Error sending image to backend:", error);
    }
  };

  const handleReactivateVideo = () => {
    if (currentImage) {
      setImageStack((prev) => [currentImage, ...prev].slice(0, 5));
    }
    setCurrentImage(null);
    setIsVideoActive(true);
    setRecognizedUser(null);
    setIsQRDialogOpen(false);
  };

  const handleEndSession = async () => {
    try {
      if (recognizedUser && recognizedUser.qr_code) {
        const sessionId = recognizedUser.qr_code.split("/").pop();
        await axios.post(`http://localhost:5000/api/end-session/${sessionId}`, {
          username,
          password,
        });
        console.log("Session ended successfully");
        setIsQRDialogOpen(false);
        handleReactivateVideo();
      }
    } catch (error) {
      console.error("Error ending session:", error);
    }
  };

  return (
    <div className="face-recognition p-4">
      <Card className="mb-4">
        <div className="relative" style={{ height: "480px" }}>
          {isVideoActive ? (
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
          ) : (
            currentImage && (
              <img
                src={currentImage}
                alt="Recognized face"
                className="w-full h-full object-cover"
                onError={(e) => {
                  console.error(`Failed to load image: ${currentImage}`);
                  e.currentTarget.src = "path/to/fallback/image.jpg";
                }}
              />
            )
          )}
        </div>
        {!isVideoActive && (
          <Button
            onClick={handleReactivateVideo}
            className="mt-2"
            intent="primary"
          >
            Reactivate Video
          </Button>
        )}
      </Card>
      {recognizedUser && (
        <Card className="mb-4">
          <h3>Recognized User</h3>
          <p>Name: {recognizedUser.name}</p>
          <p>Student ID: {recognizedUser.student_id}</p>
          {recognizedUser.qr_code && (
            <div className="mt-4">
              <h4>Session QR Code</h4>
              <img
                src={`data:image/png;base64,${recognizedUser.qr_code}`}
                alt="Session QR Code"
              />
              <Button
                onClick={() => handleQRCodeScan(recognizedUser.qr_code!)}
                intent="primary"
                className="mt-2"
              >
                End Session
              </Button>
            </div>
          )}
        </Card>
      )}
      <div className="image-stack grid grid-cols-5 gap-2">
        {imageStack.map((img, index) => (
          <div key={index} className="relative">
            <img
              src={img}
              alt={`Recognized face ${index}`}
              className="w-full h-auto"
              onError={(e) => {
                console.error(`Failed to load image: ${img}`);
                e.currentTarget.src = "path/to/fallback/image.jpg";
              }}
            />
            {recognizedUser && index === 0 && (
              <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white p-1 text-xs">
                {recognizedUser.name}
              </div>
            )}
          </div>
        ))}
      </div>
      <Dialog
        isOpen={isQRDialogOpen}
        onClose={() => setIsQRDialogOpen(false)}
        title="End Session"
      >
        <div className="p-4">
          {recognizedUser && recognizedUser.qr_code && (
            <img
              src={`data:image/png;base64,${recognizedUser.qr_code}`}
              alt="QR Code"
            />
          )}
          <FormGroup label="Username" labelFor="username-input">
            <InputGroup
              id="username-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </FormGroup>
          <FormGroup label="Password" labelFor="password-input">
            <InputGroup
              id="password-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </FormGroup>
          <Button onClick={handleEndSession} intent="primary">
            End Session
          </Button>
        </div>
      </Dialog>
    </div>
  );
};

export default FaceRecognition;

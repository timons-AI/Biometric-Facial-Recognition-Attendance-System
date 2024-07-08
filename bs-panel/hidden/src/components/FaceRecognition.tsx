import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";
import axios from "axios";
import { Card, Button, InputGroup } from "@blueprintjs/core";
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
  const [recognizedUser, setRecognizedUser] =
    useState<RecognitionResult | null>(null);
  const [qrUrl, setQrUrl] = useState<string>("");

  const navigate = useNavigate();

  // Configuration variables
  const CAPTURE_INTERVAL = 1000; // Capture interval in milliseconds

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
          const url = `http://localhost:3000/end-session/${response.data.qr_code
            .split("/")
            .pop()}`;
          setQrUrl(url);
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
    setQrUrl("");
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
              <InputGroup
                value={qrUrl}
                readOnly
                rightElement={
                  <Button
                    minimal={true}
                    onClick={() => navigator.clipboard.writeText(qrUrl)}
                  >
                    Copy
                  </Button>
                }
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
    </div>
  );
};

export default FaceRecognition;

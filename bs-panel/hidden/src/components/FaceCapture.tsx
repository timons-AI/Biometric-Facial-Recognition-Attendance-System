// components/FaceCapture.tsx
import React, { useRef, useState, useEffect } from "react";
import { Button, Card, H5, Intent } from "@blueprintjs/core";

interface FaceCaptureProps {
  onCapture: (images: File[]) => void;
  singleCapture?: boolean;
}

const FaceCapture: React.FC<FaceCaptureProps> = ({
  onCapture,
  singleCapture = false,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [capturedImages, setCapturedImages] = useState<File[]>([]);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      const s = await navigator.mediaDevices.getUserMedia({ video: true });
      setStream(s);
      if (videoRef.current) {
        videoRef.current.srcObject = s;
      }
    } catch (error) {
      console.error("Error accessing camera:", error);
    }
  };

  const captureImage = () => {
    if (videoRef.current) {
      const canvas = document.createElement("canvas");
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      canvas.getContext("2d")?.drawImage(videoRef.current, 0, 0);
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], `captured-image-${Date.now()}.jpg`, {
            type: "image/jpeg",
          });
          const newImages = [...capturedImages, file];
          setCapturedImages(newImages);
          onCapture(newImages);
          console.log(`Captured image: ${file.name}, size: ${file.size} bytes`);
          if (singleCapture) {
            stopCamera();
          }
        }
      }, "image/jpeg");
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
  };

  const removeImage = (index: number) => {
    const newImages = capturedImages.filter((_, i) => i !== index);
    setCapturedImages(newImages);
    onCapture(newImages);
  };

  return (
    <div>
      <video
        ref={videoRef}
        autoPlay
        style={{ width: "100%", maxWidth: "500px" }}
      />
      <div className=" p-2 gap-1 flex">
        <Button
          onClick={startCamera}
          disabled={!!stream}
          intent={Intent.PRIMARY}
        >
          Start Camera
        </Button>
        <Button
          onClick={captureImage}
          disabled={!stream}
          intent={Intent.SUCCESS}
        >
          Capture
        </Button>
        <Button onClick={stopCamera} disabled={!stream} intent={Intent.DANGER}>
          Stop Camera
        </Button>
      </div>
      <div style={{ marginTop: "20px" }}>
        <H5>Captured Images:</H5>
        <div style={{ display: "flex", flexWrap: "wrap" }}>
          {capturedImages.map((image, index) => (
            <Card key={index} style={{ margin: "10px", width: "150px" }}>
              <img
                src={URL.createObjectURL(image)}
                alt={`Captured ${index}`}
                style={{ width: "100%" }}
              />
              <Button
                onClick={() => removeImage(index)}
                intent={Intent.DANGER}
                small
              >
                Remove
              </Button>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FaceCapture;

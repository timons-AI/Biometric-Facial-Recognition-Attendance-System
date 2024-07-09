import React, { useState, useRef, useEffect } from "react";
import {
  Card,
  FormGroup,
  Button,
  Intent,
  HTMLSelect,
  Alert,
  Callout,
  H5,
} from "@blueprintjs/core";
import {
  getActiveCourses,
  startStudentSession,
  endStudentSession,
  checkActiveSession,
} from "../../services/api";

export interface Course {
  id: string;
  name: string;
}

export interface ActiveSession {
  session_id: string;
  course_name: string;
  start_time: string;
  qr_code: string;
}

const StartSessionPage: React.FC = () => {
  const [courseId, setCourseId] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [courses, setCourses] = useState<Course[]>([]);
  const [activeSession, setActiveSession] = useState<ActiveSession | null>(
    null
  );
  const [isAlertOpen, setIsAlertOpen] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const session = await checkActiveSession();
        if (session) {
          setActiveSession(session);
        } else {
          const activeCourses = await getActiveCourses();
          if (activeCourses.length > 0) {
            setCourses(activeCourses);
          } else {
            setError("There are no active courses at the moment.");
          }
        }
      } catch (error) {
        console.error("Error fetching initial data:", error);
        setError("Failed to fetch initial data. Please try again.");
      }
    };
    fetchInitialData();

    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      const newStream = await navigator.mediaDevices.getUserMedia({
        video: true,
      });
      setStream(newStream);
      if (videoRef.current) {
        videoRef.current.srcObject = newStream;
      }
      console.log("Camera started successfully");
    } catch (err) {
      console.error("Failed to start camera:", err);
      setError("Failed to start camera. Please check your permissions.");
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    console.log("Camera stopped");
  };

  const captureImage = () => {
    if (videoRef.current) {
      const canvas = document.createElement("canvas");
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      canvas.getContext("2d")?.drawImage(videoRef.current, 0, 0);
      const imageDataUrl = canvas.toDataURL("image/jpeg");
      setCapturedImage(imageDataUrl);
      console.log("Image captured");
      stopCamera();
    }
  };

  const handleStartSession = async () => {
    setError("");
    try {
      if (!capturedImage) {
        setError("Please capture an image before starting the session.");
        return;
      }

      const response = await startStudentSession(courseId, capturedImage);
      setActiveSession({
        session_id: response.session_id,
        course_name: courses.find((c) => c.id === courseId)?.name || "",
        start_time: new Date().toLocaleString(),
        qr_code: response.qr_code,
      });
    } catch (error: any) {
      console.error("Error starting session:", error);
      setError(
        error.response?.data?.error ||
          "Failed to start session. Please try again."
      );
    }
  };

  const handleEndSession = async () => {
    if (activeSession) {
      try {
        await endStudentSession(activeSession.session_id);
        setActiveSession(null);
        setIsAlertOpen(false);
        setCapturedImage(null);
        const activeCourses = await getActiveCourses();
        setCourses(activeCourses);
      } catch (error: any) {
        console.error("Error ending session:", error);
        setError(
          error.response?.data?.error ||
            "Failed to end session. Please try again."
        );
      }
    }
  };

  return (
    <Card className="w-1/2 mx-auto mt-10">
      <h2 className="text-2xl font-bold mb-4">Start Session</h2>
      {error && (
        <Callout intent={Intent.DANGER} title="Error" className="mb-4">
          {error}
        </Callout>
      )}

      {activeSession ? (
        <div>
          <h3 className="text-xl font-bold mb-2">Active Session</h3>
          <p>Course: {activeSession.course_name}</p>
          <p>Started at: {activeSession.start_time}</p>
          <img
            src={activeSession.qr_code}
            alt="Session QR Code"
            className="my-4"
          />
          <Button
            intent={Intent.DANGER}
            onClick={() => setIsAlertOpen(true)}
            text="End Session"
          />

          <Alert
            cancelButtonText="Cancel"
            confirmButtonText="End Session"
            icon="warning-sign"
            intent={Intent.DANGER}
            isOpen={isAlertOpen}
            onCancel={() => setIsAlertOpen(false)}
            onConfirm={handleEndSession}
          >
            <p>Are you sure you want to end this session?</p>
          </Alert>
        </div>
      ) : courses.length > 0 ? (
        <>
          <FormGroup label="Select Course" labelFor="course-select">
            <HTMLSelect
              id="course-select"
              value={courseId}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                setCourseId(e.target.value)
              }
              options={[
                { label: "Select a course", value: "" },
                ...courses.map((course) => ({
                  label: course.name,
                  value: course.id,
                })),
              ]}
            />
          </FormGroup>
          <div className="mb-4">
            <video
              ref={videoRef}
              autoPlay
              style={{
                width: "100%",
                maxWidth: "500px",
                display: stream ? "block" : "none",
              }}
            />
            {capturedImage && (
              <div>
                <H5>Captured Image:</H5>
                <img
                  src={capturedImage}
                  alt="Captured"
                  style={{ width: "100%", maxWidth: "500px" }}
                />
              </div>
            )}
            <div className="p-2 gap-1 flex">
              <Button
                onClick={startCamera}
                disabled={!!stream}
                intent={Intent.PRIMARY}
                text="Start Camera"
              />
              <Button
                onClick={captureImage}
                disabled={!stream}
                intent={Intent.SUCCESS}
                text="Capture"
              />
              <Button
                onClick={stopCamera}
                disabled={!stream}
                intent={Intent.DANGER}
                text="Stop Camera"
              />
            </div>
          </div>
          <Button
            intent={Intent.SUCCESS}
            onClick={handleStartSession}
            text="Start Session"
            disabled={!courseId || !capturedImage}
          />
        </>
      ) : (
        <p>There are no active courses at the moment.</p>
      )}
    </Card>
  );
};

export default StartSessionPage;

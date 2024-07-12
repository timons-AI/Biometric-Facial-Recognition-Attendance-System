import React, { useState, useEffect, useRef } from "react";
import { Card, Callout, H3, Intent, Spinner, Tag } from "@blueprintjs/core";
import api from "../api/api";

interface NextLecture {
  course: string;
  day: string;
  date: string;
  start_time: string;
  time_until: string;
}

interface AttendanceStatus {
  message: string;
  warning?: string;
  student_name?: string;
  course?: string;
  start_time?: string;
  end_time?: string;
  next_lecture?: NextLecture;
}

const StudentViewPortal: React.FC = () => {
  const [attendanceStatus, setAttendanceStatus] =
    useState<AttendanceStatus | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [warning, setWarning] = useState<string | null>(null);

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  useEffect(() => {
    const intervalId = setInterval(captureAndSendImage, 2000);
    return () => clearInterval(intervalId);
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      streamRef.current = stream;
    } catch (err) {
      console.error("Failed to start camera:", err);
      setError("Failed to start camera. Please check your permissions.");
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const captureAndSendImage = () => {
    if (videoRef.current && canvasRef.current && !isProcessing) {
      const context = canvasRef.current.getContext("2d");
      if (context) {
        context.drawImage(
          videoRef.current,
          0,
          0,
          canvasRef.current.width,
          canvasRef.current.height
        );
        const imageData = canvasRef.current.toDataURL("image/jpeg");
        sendImageToBackend(imageData);
      }
    }
  };

  const sendImageToBackend = async (imageData: string) => {
    try {
      setIsProcessing(true);
      setError(null);
      setWarning(null);
      const response = await api.post("/check-attendance", {
        image: imageData,
      });
      if (response.data.warning) {
        setWarning(response.data.warning);
      } else {
        setAttendanceStatus(response.data);
      }
    } catch (err: any) {
      console.error("Error processing attendance:", err);
      setError(
        err.response?.data?.error ||
          "Failed to process attendance. Please try again."
      );
      setAttendanceStatus(null);
    } finally {
      setIsProcessing(false);
    }
  };
  const getCalloutIntent = (message: string): Intent => {
    if (
      message.includes("Session ended") ||
      message.includes("Attendance recorded")
    ) {
      return Intent.SUCCESS;
    } else if (
      message.includes("Active session") ||
      message.includes("Early for next class")
    ) {
      return Intent.PRIMARY;
    } else {
      return Intent.NONE;
    }
  };

  const renderAttendanceStatus = () => {
    if (!attendanceStatus) return null;

    return (
      <Callout
        intent={getCalloutIntent(attendanceStatus.message)}
        title="Attendance Status"
        className="mb-4"
      >
        <p>
          <strong>{attendanceStatus.student_name}</strong>
        </p>
        <p>{attendanceStatus.message}</p>
        {attendanceStatus.course && <p>Course: {attendanceStatus.course}</p>}
        {attendanceStatus.start_time && (
          <p>Starts at: {attendanceStatus.start_time}</p>
        )}
        {attendanceStatus.end_time && (
          <p>Ends at: {attendanceStatus.end_time}</p>
        )}
        {attendanceStatus.next_lecture && (
          <div>
            <p>Next Scheduled Lecture:</p>
            <p>Course: {attendanceStatus.next_lecture.course}</p>
            <p>Day: {attendanceStatus.next_lecture.day}</p>
            <p>Date: {attendanceStatus.next_lecture.date}</p>
            <p>Start Time: {attendanceStatus.next_lecture.start_time}</p>
            <p>
              Time Until:{" "}
              <Tag minimal intent="warning">
                {attendanceStatus.next_lecture.time_until}
              </Tag>
            </p>
          </div>
        )}
      </Callout>
    );
  };

  return (
    <div className="p-4">
      <Card elevation={2}>
        <H3>Attendance Check-In Portal</H3>
        {error && (
          <Callout intent={Intent.DANGER} title="Error" className="mb-4">
            {error}
          </Callout>
        )}
        {warning && (
          <Callout intent={Intent.WARNING} title="Warning" className="mb-4">
            {warning}
          </Callout>
        )}
        {renderAttendanceStatus()}
        <div className="mb-4 relative">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{ width: "100%", maxWidth: "640px" }}
          />
          {isProcessing && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
              <Spinner intent={Intent.PRIMARY} size={50} />
            </div>
          )}
        </div>
        <canvas
          ref={canvasRef}
          style={{ display: "none" }}
          width={640}
          height={480}
        />
      </Card>
    </div>
  );
};

export default StudentViewPortal;

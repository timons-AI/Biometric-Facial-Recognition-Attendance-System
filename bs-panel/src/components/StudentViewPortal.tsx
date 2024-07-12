import React, { useState, useEffect, useRef } from "react";
import { Card, Callout, H3, H4, Intent, Spinner, Tag } from "@blueprintjs/core";
import api from "../api/api";

interface ClassInfo {
  course: string;
  start_time: string;
  end_time: string;
  room: string;
}

interface NextLecture extends ClassInfo {
  day: string;
  date: string;
  time_until: string;
}

interface WeeklySchedule {
  day: string;
  course: string;
  start_time: string;
  end_time: string;
  room: string;
}

interface AttendanceStatus {
  message: string;
  warning?: string;
  student_name?: string;
  current_time?: string;
  active_session?: ClassInfo | null;
  next_lecture?: NextLecture | null;
  weekly_schedule?: WeeklySchedule[];
}

const StudentViewPortal: React.FC = () => {
  const [attendanceStatus, setAttendanceStatus] =
    useState<AttendanceStatus | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  useEffect(() => {
    const intervalId = setInterval(captureAndSendImage, 2000); // Capture every 5 seconds
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
      const response = await api.post("/check-attendance", {
        image: imageData,
      });
      setAttendanceStatus(response.data);
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

  const getCalloutIntent = (status: AttendanceStatus): Intent => {
    if (status.warning) return Intent.WARNING;
    if (
      status.message.includes("Session ended") ||
      status.message.includes("Attendance recorded")
    ) {
      return Intent.SUCCESS;
    } else if (
      status.message.includes("Active session") ||
      status.message.includes("Next class starts in")
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
        intent={getCalloutIntent(attendanceStatus)}
        title="Attendance Status"
        className="mb-4"
      >
        {attendanceStatus.warning ? (
          <p>{attendanceStatus.warning}</p>
        ) : (
          <>
            {attendanceStatus.student_name && (
              <H3>{attendanceStatus.student_name}</H3>
            )}
            {attendanceStatus.current_time && (
              <p>Current Time: {attendanceStatus.current_time}</p>
            )}
            <p>{attendanceStatus.message}</p>

            {attendanceStatus.active_session && (
              <div>
                <H4>Active Session</H4>
                <p>Course: {attendanceStatus.active_session.course}</p>
                <p>Start Time: {attendanceStatus.active_session.start_time}</p>
                <p>End Time: {attendanceStatus.active_session.end_time}</p>
                <p>Room: {attendanceStatus.active_session.room}</p>
              </div>
            )}

            {attendanceStatus.next_lecture && (
              <div>
                <H4>Next Scheduled Lecture</H4>
                <p>Course: {attendanceStatus.next_lecture.course}</p>
                <p>Day: {attendanceStatus.next_lecture.day}</p>
                <p>Date: {attendanceStatus.next_lecture.date}</p>
                <p>Start Time: {attendanceStatus.next_lecture.start_time}</p>
                <p>End Time: {attendanceStatus.next_lecture.end_time}</p>
                <p>Room: {attendanceStatus.next_lecture.room}</p>
                <p>
                  Time Until:{" "}
                  <Tag intent={Intent.WARNING}>
                    {attendanceStatus.next_lecture.time_until}
                  </Tag>
                </p>
              </div>
            )}

            {attendanceStatus.weekly_schedule &&
              attendanceStatus.weekly_schedule.length > 0 && (
                <>
                  <H4>Weekly Schedule</H4>
                  {attendanceStatus.weekly_schedule.map((class_, index) => (
                    <div key={index} className="mb-2">
                      <p>
                        <strong>{class_.day}</strong>: {class_.course} (
                        {class_.start_time} - {class_.end_time}) Room:{" "}
                        {class_.room}
                      </p>
                    </div>
                  ))}
                </>
              )}
          </>
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

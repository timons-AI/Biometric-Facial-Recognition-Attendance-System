import React, { useState, useEffect } from "react";
import { useAtom } from "jotai";
import { Card, H2, H4, Tag, Intent, Spinner } from "@blueprintjs/core";
import { userAtom } from "../../store/auth";
import api from "../../services/api";

interface AttendanceRecord {
  courseId: string;
  courseName: string;
  attendancePercentage: number;
  totalSessions: number;
  attendedSessions: number;
}

const StudentDashboard: React.FC = () => {
  const [user] = useAtom(userAtom);
  const [attendanceData, setAttendanceData] = useState<AttendanceRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAttendanceData = async () => {
      try {
        const response = await api.get(`/student/attendance/${user?.id}`);
        setAttendanceData(response.data);
      } catch (error) {
        console.error("Failed to fetch attendance data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAttendanceData();
  }, [user]);

  if (isLoading) {
    return <Spinner />;
  }

  const overallAttendance =
    attendanceData.reduce(
      (sum, record) => sum + record.attendancePercentage,
      0
    ) / attendanceData.length;

  return (
    <div>
      <H2>Student Dashboard</H2>
      <Card elevation={2}>
        <H4>User Information</H4>
        <p>Name: {user?.name}</p>
        <p>ID: {user?.id}</p>
        <p>Overall Attendance: {overallAttendance.toFixed(2)}%</p>
      </Card>
      <H4 className="mt-4">Course Attendance</H4>
      {attendanceData.map((record) => (
        <Card key={record.courseId} elevation={2} className="mt-2">
          <H4>{record.courseName}</H4>
          <p>Attendance: {record.attendancePercentage.toFixed(2)}%</p>
          <p>
            Sessions Attended: {record.attendedSessions} /{" "}
            {record.totalSessions}
          </p>
          <Tag
            intent={
              record.attendancePercentage >= 75 ? Intent.SUCCESS : Intent.DANGER
            }
          >
            {record.attendancePercentage >= 75
              ? "Good Standing"
              : "Attention Required"}
          </Tag>
        </Card>
      ))}
    </div>
  );
};

export default StudentDashboard;

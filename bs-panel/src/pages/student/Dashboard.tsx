import React, { useState, useEffect } from "react";
import { Card, Elevation, Button, Icon } from "@blueprintjs/core";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import QRCode from "qrcode.react";
import { fetchStudentDashboardData } from "../../services/api";
import { Cell, Column, Table2 } from "@blueprintjs/table";

// Make sure to import the CSS
import "@blueprintjs/table/lib/css/table.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export interface DashboardData {
  activeSession: {
    session_id: string;
    course_name: string;
    lecturer_name: string;
    start_time: string;
    end_time: string;
    qr_code: string;
  } | null;
  attendanceStats: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      borderColor: string;
      backgroundColor: string;
    }[];
  };
  timetable: {
    day: string;
    courses: {
      course_name: string;
      start_time: string;
      end_time: string;
      lecturer_name: string;
    }[];
  }[];
  totalAttendance: number;
  totalCourses: number;
  currentDay: string;
  currentTimestamp: string;
}

const StudentDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(
    null
  );
  const [countdown, setCountdown] = useState<string>("");
  const [currentTime, setCurrentTime] = useState<Date>(new Date());

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await fetchStudentDashboardData();
        setDashboardData(data);
        setCurrentTime(new Date(data.currentTimestamp));
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5 * 60 * 1000); // Fetch every 5 minutes

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime((prevTime) => new Date(prevTime.getTime() + 1000));
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (dashboardData?.activeSession) {
      const timer = setInterval(() => {
        const now = currentTime;
        const end = new Date(dashboardData.activeSession!.end_time);
        const diff = end.getTime() - now.getTime();

        if (diff > 0) {
          const hours = Math.floor(diff / (1000 * 60 * 60));
          const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
          const seconds = Math.floor((diff % (1000 * 60)) / 1000);
          setCountdown(`${hours}h ${minutes}m ${seconds}s`);
        } else {
          setCountdown("Session ended");
          clearInterval(timer);
        }
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [dashboardData, currentTime]);

  if (!dashboardData) return <div>Loading...</div>;

  const isCurrentlyActive = (startTime: string, endTime: string): boolean => {
    const now = currentTime;
    const [startHour, startMinute] = startTime.split(":").map(Number);
    const [endHour, endMinute] = endTime.split(":").map(Number);
    const start = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate(),
      startHour,
      startMinute
    );
    const end = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate(),
      endHour,
      endMinute
    );
    return now >= start && now <= end;
  };

  const renderDayCell = (rowIndex: number) => (
    <Cell>
      <div
        className={
          dashboardData.currentDay === dashboardData.timetable[rowIndex].day
            ? "font-bold text-blue-600"
            : ""
        }
      >
        {dashboardData.timetable[rowIndex].day}
      </div>
    </Cell>
  );

  const renderCourseCell = (rowIndex: number) => (
    <Cell>
      {dashboardData.timetable[rowIndex].courses.map((course, index) => (
        <div key={index}>
          {course.course_name}
          {isCurrentlyActive(course.start_time, course.end_time) && (
            <Icon icon="star" intent="primary" className="ml-2" />
          )}
        </div>
      ))}
    </Cell>
  );

  const renderTimeCell = (rowIndex: number) => (
    <Cell>
      {dashboardData.timetable[rowIndex].courses.map((course, index) => {
        const isActive = isCurrentlyActive(course.start_time, course.end_time);
        return (
          <div
            key={index}
            style={{ backgroundColor: isActive ? "#e3f2fd" : undefined }}
          >
            {`${course.start_time} - ${course.end_time}`}
          </div>
        );
      })}
    </Cell>
  );

  const renderLecturerCell = (rowIndex: number) => (
    <Cell>
      {dashboardData.timetable[rowIndex].courses.map((course, index) => (
        <div key={index}>{course.lecturer_name}</div>
      ))}
    </Cell>
  );

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Student Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <Card elevation={Elevation.TWO}>
          <h2 className="text-xl font-semibold mb-2">Statistics</h2>
          <p>Total Attendance: {dashboardData.totalAttendance}</p>
          <p>Total Course Units: {dashboardData.totalCourses}</p>
          <p>Current Time: {currentTime.toLocaleTimeString()}</p>
          <p>Current Day: {dashboardData.currentDay}</p>
        </Card>

        {dashboardData.activeSession && (
          <Card elevation={Elevation.TWO}>
            <h2 className="text-xl font-semibold mb-2">Active Session</h2>
            <p>Course Unit: {dashboardData.activeSession.course_name}</p>
            <p>Lecturer: {dashboardData.activeSession.lecturer_name}</p>
            <p>
              Start Time:{" "}
              {new Date(
                dashboardData.activeSession.start_time
              ).toLocaleTimeString()}
            </p>
            <p>
              End Time:{" "}
              {new Date(
                dashboardData.activeSession.end_time
              ).toLocaleTimeString()}
            </p>
            <p>Time Remaining: {countdown}</p>
            <div className="mt-2">
              <QRCode value={dashboardData.activeSession.qr_code} size={128} />
            </div>
          </Card>
        )}
      </div>

      <Card elevation={Elevation.TWO} className="mb-4">
        <h2 className="text-xl font-semibold mb-2">Attendance History</h2>
        <Line
          data={dashboardData.attendanceStats}
          options={{
            responsive: true,
            plugins: {
              legend: {
                position: "top" as const,
              },
              title: {
                display: true,
                text: "Attendance History",
              },
            },
          }}
        />
      </Card>

      <Card elevation={Elevation.TWO}>
        <h2 className="text-xl font-semibold mb-2">Timetable</h2>
        <Table2 numRows={dashboardData.timetable.length}>
          <Column name="Day" cellRenderer={renderDayCell} />
          <Column name="Course Unit" cellRenderer={renderCourseCell} />
          <Column name="Time" cellRenderer={renderTimeCell} />
          <Column name="Lecturer" cellRenderer={renderLecturerCell} />
        </Table2>
      </Card>
    </div>
  );
};

export default StudentDashboard;

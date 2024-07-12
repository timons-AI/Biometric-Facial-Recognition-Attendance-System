import React, { useState, useEffect } from "react";
import {
  Card,
  Elevation,
  H3,
  H5,
  Tag,
  Spinner,
  Intent,
  Callout,
} from "@blueprintjs/core";
import { Cell, Column, Table2 } from "@blueprintjs/table";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import api from "../api/api";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface TimetableEntry {
  day: string;
  start_time: string;
  end_time: string;
  course_name: string;
  lecturer_name: string;
}

interface AttendanceStats {
  total_classes: number;
  classes_attended: number;
  attendance_percentage: number;
}

interface StudentDashboardData {
  student_name: string;
  timetable: TimetableEntry[];
  attendance_stats: AttendanceStats;
  upcoming_classes: TimetableEntry[];
}

const StudentDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] =
    useState<StudentDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get("/student/dashboard");
      setDashboardData(response.data);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
      setError("Failed to load dashboard data. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Spinner size={50} />;
  }

  if (error) {
    return <Callout intent={Intent.DANGER}>{error}</Callout>;
  }

  if (!dashboardData) {
    return (
      <Callout intent={Intent.WARNING}>No dashboard data available.</Callout>
    );
  }

  const { student_name, timetable, attendance_stats, upcoming_classes } =
    dashboardData;

  const attendanceChartData = {
    labels: ["Attended", "Missed"],
    datasets: [
      {
        label: "Classes",
        data: [
          attendance_stats.classes_attended,
          attendance_stats.total_classes - attendance_stats.classes_attended,
        ],
        backgroundColor: ["rgba(75, 192, 192, 0.6)", "rgba(255, 99, 132, 0.6)"],
      },
    ],
  };

  const renderDayCell = (rowIndex: number) => (
    <Cell>{timetable[rowIndex].day}</Cell>
  );

  const renderTimeCell = (rowIndex: number) => (
    <Cell>{`${timetable[rowIndex].start_time} - ${timetable[rowIndex].end_time}`}</Cell>
  );

  const renderCourseCell = (rowIndex: number) => (
    <Cell>{timetable[rowIndex].course_name}</Cell>
  );

  const renderLecturerCell = (rowIndex: number) => (
    <Cell>{timetable[rowIndex].lecturer_name}</Cell>
  );

  return (
    <div className="p-4">
      <H3>Welcome, {student_name}</H3>

      <Card elevation={Elevation.TWO} className="mt-4">
        <H5>Attendance Statistics</H5>
        <p>Total Classes: {attendance_stats.total_classes}</p>
        <p>Classes Attended: {attendance_stats.classes_attended}</p>
        <p>
          Attendance Percentage:{" "}
          {attendance_stats.attendance_percentage.toFixed(2)}%
        </p>
        <div style={{ height: "300px" }}>
          <Bar
            data={attendanceChartData}
            options={{ maintainAspectRatio: false }}
          />
        </div>
      </Card>

      <Card elevation={Elevation.TWO} className="mt-4">
        <H5>Your Timetable</H5>
        <Table2 numRows={timetable.length}>
          <Column name="Day" cellRenderer={renderDayCell} />
          <Column name="Time" cellRenderer={renderTimeCell} />
          <Column name="Course" cellRenderer={renderCourseCell} />
          <Column name="Lecturer" cellRenderer={renderLecturerCell} />
        </Table2>
      </Card>

      <Card elevation={Elevation.TWO} className="mt-4">
        <H5>Upcoming Classes</H5>
        {upcoming_classes.map((class_, index) => (
          <Card key={index} className="mb-2">
            <H5>{class_.course_name}</H5>
            <p>Day: {class_.day}</p>
            <p>
              Time: {class_.start_time} - {class_.end_time}
            </p>
            <p>Lecturer: {class_.lecturer_name}</p>
            <Tag intent={Intent.PRIMARY}>Upcoming</Tag>
          </Card>
        ))}
      </Card>
    </div>
  );
};

export default StudentDashboard;

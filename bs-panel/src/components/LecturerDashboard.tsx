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
  room: string;
}

interface CourseStats {
  course_name: string;
  total_students: number;
  total_attendances: number;
  attendance_rate: number;
}

interface LecturerDashboardData {
  lecturer_name: string;
  timetable: TimetableEntry[];
  upcoming_classes: TimetableEntry[];
  course_stats: CourseStats[];
}

const LecturerDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] =
    useState<LecturerDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get("/lecturer/dashboard");
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

  const { lecturer_name, timetable, upcoming_classes, course_stats } =
    dashboardData;

  const attendanceChartData = {
    labels: course_stats.map((stat) => stat.course_name),
    datasets: [
      {
        label: "Attendance Rate",
        data: course_stats.map((stat) => stat.attendance_rate),
        backgroundColor: "rgba(75, 192, 192, 0.6)",
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

  const renderRoomCell = (rowIndex: number) => (
    <Cell>{timetable[rowIndex].room}</Cell>
  );

  return (
    <div className="p-4">
      <H3>Welcome, {lecturer_name}</H3>

      <Card elevation={Elevation.TWO} className="mt-4">
        <H5>Course Statistics</H5>
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
          <Column name="Room" cellRenderer={renderRoomCell} />
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
            <p>Room: {class_.room}</p>
            <Tag intent={Intent.PRIMARY}>Upcoming</Tag>
          </Card>
        ))}
      </Card>
    </div>
  );
};

export default LecturerDashboard;

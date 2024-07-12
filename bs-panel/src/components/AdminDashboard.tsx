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
import { Bar, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import api from "../api/api";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface OverallStats {
  total_students: number;
  total_lecturers: number;
  total_courses: number;
  total_attendances: number;
}

interface RecentRegistration {
  name: string;
  role: string;
  email: string;
  date: string;
}

interface TopCourse {
  name: string;
  attendance_rate: number;
}

interface TopLecturer {
  name: string;
  class_count: number;
}

interface AdminDashboardData {
  admin_name: string;
  overall_stats: OverallStats;
  recent_registrations: RecentRegistration[];
  top_courses: TopCourse[];
  top_lecturers: TopLecturer[];
}

const AdminDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<AdminDashboardData | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get("/admin/dashboard");
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

  const {
    admin_name,
    overall_stats,
    recent_registrations,
    top_courses,
    top_lecturers,
  } = dashboardData;

  const courseAttendanceData = {
    labels: top_courses.map((course) => course.name),
    datasets: [
      {
        label: "Attendance Rate",
        data: top_courses.map((course) => course.attendance_rate),
        backgroundColor: "rgba(75, 192, 192, 0.6)",
      },
    ],
  };

  const overallStatsData = {
    labels: ["Students", "Lecturers", "Courses", "Attendances"],
    datasets: [
      {
        data: [
          overall_stats.total_students,
          overall_stats.total_lecturers,
          overall_stats.total_courses,
          overall_stats.total_attendances,
        ],
        backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"],
        hoverBackgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"],
      },
    ],
  };

  return (
    <div className="p-4">
      <H3>Welcome, {admin_name}</H3>

      <Card elevation={Elevation.TWO} className="mt-4">
        <H5>Overall Statistics</H5>
        <div style={{ height: "300px" }}>
          <Doughnut
            data={overallStatsData}
            options={{ maintainAspectRatio: false }}
          />
        </div>
      </Card>

      <Card elevation={Elevation.TWO} className="mt-4">
        <H5>Top Courses by Attendance Rate</H5>
        <div style={{ height: "300px" }}>
          <Bar
            data={courseAttendanceData}
            options={{ maintainAspectRatio: false }}
          />
        </div>
      </Card>

      <Card elevation={Elevation.TWO} className="mt-4">
        <H5>Recent Registrations</H5>
        <Table2 numRows={recent_registrations.length}>
          <Column
            name="Name"
            cellRenderer={(rowIndex) => (
              <Cell>{recent_registrations[rowIndex].name}</Cell>
            )}
          />
          <Column
            name="Role"
            cellRenderer={(rowIndex) => (
              <Cell>{recent_registrations[rowIndex].role}</Cell>
            )}
          />
          <Column
            name="Email"
            cellRenderer={(rowIndex) => (
              <Cell>{recent_registrations[rowIndex].email}</Cell>
            )}
          />
          {/* <Column
            name="Date"
            cellRenderer={(rowIndex) => (
              <Cell>{recent_registrations[rowIndex].date}</Cell>
            )}
          /> */}
        </Table2>
      </Card>

      <Card elevation={Elevation.TWO} className="mt-4">
        <H5>Top Lecturers by Class Count</H5>
        <Table2 numRows={top_lecturers.length}>
          <Column
            name="Name"
            cellRenderer={(rowIndex) => (
              <Cell>{top_lecturers[rowIndex].name}</Cell>
            )}
          />
          <Column
            name="Class Count"
            cellRenderer={(rowIndex) => (
              <Cell>{top_lecturers[rowIndex].class_count}</Cell>
            )}
          />
        </Table2>
      </Card>
    </div>
  );
};

export default AdminDashboard;

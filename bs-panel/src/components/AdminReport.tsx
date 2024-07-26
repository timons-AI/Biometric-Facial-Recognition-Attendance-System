import React, { useState, useEffect } from "react";
import {
  Card,
  Elevation,
  H3,
  H5,
  Spinner,
  Intent,
  Callout,
  Tab,
  Tabs,
} from "@blueprintjs/core";
import { Cell, Column, Table2 } from "@blueprintjs/table";
import { Bar, Doughnut, Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions,
} from "chart.js";
import api from "../api/api";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface College {
  name: string;
  attendance_rate: number;
}

interface AttendanceTrend {
  date: string;
  total_sessions: number;
  attended_sessions: number;
}

interface Course {
  name: string;
  attendance_rate: number;
}

interface LecturerPerformance {
  lecturer_name: string;
  total_sessions: number;
  average_attendance_rate: number;
}

interface StudentEngagement {
  student_name: string;
  total_sessions: number;
  attended_sessions: number;
  attendance_rate: number;
}

interface AdminReports {
  overall_attendance_rate: number;
  attendance_by_college: College[];
  attendance_trends: AttendanceTrend[];
  top_attending_courses: Course[];
  low_attending_courses: Course[];
  lecturer_performance: LecturerPerformance[];
  student_engagement: StudentEngagement[];
}

const AdminReportsDashboard: React.FC = () => {
  const [reports, setReports] = useState<AdminReports | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const response = await api.get<AdminReports>("/admin/reports");
      setReports(response.data);
    } catch (err) {
      console.error("Error fetching reports:", err);
      setError("Failed to load reports. Please try again later.");
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

  if (!reports) {
    return <Callout intent={Intent.WARNING}>No report data available.</Callout>;
  }

  const {
    overall_attendance_rate,
    attendance_by_college,
    attendance_trends,
    top_attending_courses,
    low_attending_courses,
    lecturer_performance,
    student_engagement,
  } = reports;

  const overallStatsData: ChartData<"doughnut"> = {
    labels: ["Overall Attendance Rate", "Absence Rate"],
    datasets: [
      {
        data: [overall_attendance_rate, 100 - overall_attendance_rate],
        backgroundColor: ["#36A2EB", "#FFCE56"],
        hoverBackgroundColor: ["#36A2EB", "#FFCE56"],
      },
    ],
  };

  const attendanceByCollegeData: ChartData<"bar"> = {
    labels: attendance_by_college.map((college) => college.name),
    datasets: [
      {
        label: "Attendance Rate",
        data: attendance_by_college.map((college) => college.attendance_rate),
        backgroundColor: "rgba(75, 192, 192, 0.6)",
      },
    ],
  };

  const attendanceTrendsData: ChartData<"line"> = {
    labels: attendance_trends.map((trend) => trend.date),
    datasets: [
      {
        label: "Attendance Rate",
        data: attendance_trends.map(
          (trend) => (trend.attended_sessions / trend.total_sessions) * 100
        ),
        borderColor: "rgb(75, 192, 192)",
        tension: 0.1,
      },
    ],
  };

  const topCoursesData: ChartData<"bar"> = {
    labels: top_attending_courses.map((course) => course.name),
    datasets: [
      {
        label: "Attendance Rate",
        data: top_attending_courses.map((course) => course.attendance_rate),
        backgroundColor: "rgba(53, 162, 235, 0.5)",
      },
    ],
  };

  const lowCoursesData: ChartData<"bar"> = {
    labels: low_attending_courses.map((course) => course.name),
    datasets: [
      {
        label: "Attendance Rate",
        data: low_attending_courses.map((course) => course.attendance_rate),
        backgroundColor: "rgba(255, 99, 132, 0.5)",
      },
    ],
  };

  const chartOptions: ChartOptions<"bar"> = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: "Attendance Rate (%)",
        },
      },
    },
  };

  return (
    <div className="p-4">
      <H3>Admin Reports Dashboard</H3>

      <Card elevation={Elevation.TWO} className="mt-4">
        <H5>Overall Attendance Rate</H5>
        <div style={{ height: "300px" }}>
          <Doughnut
            data={overallStatsData}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                tooltip: {
                  callbacks: {
                    label: (context) => {
                      const label = context.label || "";
                      const value = (context.raw as number) || 0;
                      return `${label}: ${value.toFixed(2)}%`;
                    },
                  },
                },
              },
            }}
          />
        </div>
      </Card>

      <Card elevation={Elevation.TWO} className="mt-4">
        <H5>Attendance by College</H5>
        <div style={{ height: "300px" }}>
          <Bar data={attendanceByCollegeData} options={chartOptions} />
        </div>
      </Card>

      <Card elevation={Elevation.TWO} className="mt-4">
        <H5>Attendance Trends (Last 30 Days)</H5>
        <div style={{ height: "300px" }}>
          <Line
            data={attendanceTrendsData}
            options={{
              ...chartOptions,
              scales: {
                ...chartOptions.scales,
                x: {
                  title: {
                    display: true,
                    text: "Date",
                  },
                },
              },
            }}
          />
        </div>
      </Card>

      <Tabs id="CourseAttendanceTabs" className="mt-4">
        <Tab
          id="top"
          title="Top Attending Courses"
          panel={
            <Card elevation={Elevation.TWO}>
              <div style={{ height: "300px" }}>
                <Bar data={topCoursesData} options={chartOptions} />
              </div>
            </Card>
          }
        />
        <Tab
          id="low"
          title="Low Attending Courses"
          panel={
            <Card elevation={Elevation.TWO}>
              <div style={{ height: "300px" }}>
                <Bar data={lowCoursesData} options={chartOptions} />
              </div>
            </Card>
          }
        />
      </Tabs>

      <Card elevation={Elevation.TWO} className="mt-4">
        <H5>Lecturer Performance</H5>
        <Table2 numRows={lecturer_performance.length}>
          <Column
            name="Lecturer Name"
            cellRenderer={(rowIndex) => (
              <Cell>{lecturer_performance[rowIndex].lecturer_name}</Cell>
            )}
          />
          <Column
            name="Total Sessions"
            cellRenderer={(rowIndex) => (
              <Cell>{lecturer_performance[rowIndex].total_sessions}</Cell>
            )}
          />
          <Column
            name="Average Attendance Rate"
            cellRenderer={(rowIndex) => (
              <Cell>{`${lecturer_performance[
                rowIndex
              ].average_attendance_rate.toFixed(2)}%`}</Cell>
            )}
          />
        </Table2>
      </Card>

      <Card elevation={Elevation.TWO} className="mt-4">
        <H5>Student Engagement</H5>
        <Table2 numRows={student_engagement.length}>
          <Column
            name="Student Name"
            cellRenderer={(rowIndex) => (
              <Cell>{student_engagement[rowIndex].student_name}</Cell>
            )}
          />
          <Column
            name="Total Sessions"
            cellRenderer={(rowIndex) => (
              <Cell>{student_engagement[rowIndex].total_sessions}</Cell>
            )}
          />
          <Column
            name="Attended Sessions"
            cellRenderer={(rowIndex) => (
              <Cell>{student_engagement[rowIndex].attended_sessions}</Cell>
            )}
          />
          <Column
            name="Attendance Rate"
            cellRenderer={(rowIndex) => (
              <Cell>{`${student_engagement[rowIndex].attendance_rate.toFixed(
                2
              )}%`}</Cell>
            )}
          />
        </Table2>
      </Card>
    </div>
  );
};

export default AdminReportsDashboard;

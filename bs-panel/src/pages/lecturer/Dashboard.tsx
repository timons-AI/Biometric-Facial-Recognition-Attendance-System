import React, { useState, useEffect } from "react";
import {
  Card,
  H2,
  H3,
  Button,
  HTMLTable,
  Spinner,
  Intent,
  Callout,
  Section,
  SectionCard,
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
import { fetchTeacherDashboardData } from "../../services/api";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface Student {
  student_id: string;
  name: string;
  email: string;
  status: "active" | "inactive";
}

interface Course {
  course_id: string;
  course_name: string;
  active_students: number;
  total_students: number;
}

interface TimetableEntry {
  day: string;
  start_time: string;
  end_time: string;
  course_name: string;
}

interface TeacherDashboardData {
  activeStudents: Student[];
  courses: Course[];
  timetable: TimetableEntry[];
  attendanceStats: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      backgroundColor: string;
    }[];
  };
}

const TeacherDashboard: React.FC = () => {
  const [data, setData] = useState<TeacherDashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const dashboardData = await fetchTeacherDashboardData();
        setData(dashboardData);
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return <Spinner />;
  }

  if (!data) {
    return <Callout intent={Intent.DANGER}>Failed to load data.</Callout>;
  }

  return (
    <div className="teacher-dashboard">
      <H2>Teacher Dashboard</H2>

      <Section
        title="Active Students"
        elevation={1}
        collapsible={true}
        icon="user"
      >
        <Table2 numRows={data.activeStudents.length}>
          <Column
            name="Student ID"
            cellRenderer={(rowIndex) => (
              <Cell>{data.activeStudents[rowIndex].student_id}</Cell>
            )}
          />
          <Column
            name="Name"
            cellRenderer={(rowIndex) => (
              <Cell>{data.activeStudents[rowIndex].name}</Cell>
            )}
          />
          <Column
            name="Email"
            cellRenderer={(rowIndex) => (
              <Cell>{data.activeStudents[rowIndex].email}</Cell>
            )}
          />
          <Column
            name="Status"
            cellRenderer={(rowIndex) => (
              <Cell>{data.activeStudents[rowIndex].status}</Cell>
            )}
          />
        </Table2>
      </Section>

      <Section title="Courses" elevation={1} collapsible={true} icon="book">
        <HTMLTable>
          <thead>
            <tr>
              <th>Course ID</th>
              <th>Course Name</th>
              <th>Active Students</th>
              <th>Total Students</th>
            </tr>
          </thead>
          <tbody>
            {data.courses.map((course) => (
              <tr key={course.course_id}>
                <td>{course.course_id}</td>
                <td>{course.course_name}</td>
                <td>{course.active_students}</td>
                <td>{course.total_students}</td>
              </tr>
            ))}
          </tbody>
        </HTMLTable>
      </Section>

      <Section
        title="Timetable"
        elevation={1}
        collapsible={true}
        icon="calendar"
      >
        <HTMLTable>
          <thead>
            <tr>
              <th>Day</th>
              <th>Start Time</th>
              <th>End Time</th>
              <th>Course</th>
            </tr>
          </thead>
          <tbody>
            {data.timetable.map((entry, index) => (
              <tr key={index}>
                <td>{entry.day}</td>
                <td>{entry.start_time}</td>
                <td>{entry.end_time}</td>
                <td>{entry.course_name}</td>
              </tr>
            ))}
          </tbody>
        </HTMLTable>
      </Section>

      <Section
        title="Attendance Statistics"
        elevation={1}
        collapsible={true}
        icon="chart"
      >
        <Bar data={data.attendanceStats} />
      </Section>

      <Section title="Actions" elevation={1}>
        <SectionCard>
          <Button
            intent={Intent.PRIMARY}
            text="End All Active Sessions"
            onClick={() => {
              /* Implement end all sessions logic */
            }}
          />
        </SectionCard>
      </Section>
    </div>
  );
};

export default TeacherDashboard;

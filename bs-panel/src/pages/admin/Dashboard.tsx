import React, { useState, useEffect, useCallback } from "react";
import {
  Card,
  H2,
  H3,
  Button,
  HTMLTable,
  Spinner,
  Intent,
  Dialog,
  FormGroup,
  InputGroup,
  Section,
  SectionCard,
  DialogBody,
  DialogFooter,
  Tag,
} from "@blueprintjs/core";
import { Cell, Column, Table2 } from "@blueprintjs/table";
import { Bar, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";
import {
  fetchAdminDashboardData,
  registerLecturer,
  addCourse,
  addTimetableEntry,
} from "../../services/api";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface Student {
  student_id: string;
  name: string;
  email: string;
  total_sessions: number;
}

interface Lecturer {
  lecturer_id: string;
  name: string;
  email: string;
  courses_count: number;
}

interface Course {
  course_id: string;
  course_name: string;
  lecturer_name: string;
  students_count: number;
}

interface AttendanceStats {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string;
  }[];
}

export interface AdminDashboardData {
  totalStudents: number;
  totalLecturers: number;
  totalCourses: number;
  recentStudents: Student[];
  topLecturers: Lecturer[];
  popularCourses: Course[];
  attendanceStats: AttendanceStats;
  courseDistribution: AttendanceStats;
}

const AdminDashboard: React.FC = () => {
  const [data, setData] = useState<AdminDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAddLecturerOpen, setIsAddLecturerOpen] = useState(false);
  const [isAddCourseOpen, setIsAddCourseOpen] = useState(false);
  const [isAddTimetableOpen, setIsAddTimetableOpen] = useState(false);

  const loadData = useCallback(async () => {
    if (!data) {
      // Only fetch if data is not already loaded
      try {
        setLoading(true);
        const dashboardData = await fetchAdminDashboardData(); // or fetchTeacherDashboardData
        setData(dashboardData);
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setLoading(false);
      }
    }
  }, [data]); // Add data as a dependency

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleAddLecturer = async (
    name: string,
    email: string,
    password: string
  ) => {
    try {
      await registerLecturer(name, email, password);
      setData(null); // Reset data to trigger a re-fetch
      loadData(); // Re-fetch data
      setIsAddLecturerOpen(false);
    } catch (error) {
      console.error("Failed to add lecturer:", error);
    }
  };

  // Apply similar changes to handleAddCourse and handleAddTimetable
  const handleAddCourse = async (courseName: string, lecturerId: string) => {
    try {
      await addCourse(courseName, lecturerId);
      setData(null);
      loadData();
      setIsAddCourseOpen(false);
    } catch (error) {
      console.error("Failed to add course:", error);
    }
  };

  const handleAddTimetable = async (
    courseId: string,
    day: string,
    startTime: string,
    endTime: string
  ) => {
    try {
      await addTimetableEntry(courseId, day, startTime, endTime);
      setData(null);
      loadData();
      setIsAddTimetableOpen(false);
    } catch (error) {
      console.error("Failed to add timetable entry:", error);
    }
  };

  if (loading) {
    return <Spinner />;
  }

  if (!data) {
    return <div>Failed to load dashboard data.</div>;
  }
  return (
    <div className="grid gap-2">
      <H2>Admin Dashboard</H2>

      <Section title="Dashboard Summary" elevation={1}>
        <SectionCard>
          <H3>Total Students</H3>
          <Tag>{data.totalStudents}</Tag>
        </SectionCard>
        <SectionCard>
          <H3>Total Lecturers</H3>
          <Tag intent="primary">{data.totalLecturers}</Tag>
        </SectionCard>
        <SectionCard>
          <H3>Total Courses</H3>
          <Tag intent="success">{data.totalCourses}</Tag>
        </SectionCard>
      </Section>

      <Section
        title="Recent Students"
        elevation={1}
        collapsible={true}
        icon="user"
      >
        <Table2 numRows={data.recentStudents.length}>
          <Column
            name="Student ID"
            cellRenderer={(rowIndex) => (
              <Cell>{data.recentStudents[rowIndex].student_id}</Cell>
            )}
          />
          <Column
            name="Name"
            cellRenderer={(rowIndex) => (
              <Cell>{data.recentStudents[rowIndex].name}</Cell>
            )}
          />
          <Column
            name="Email"
            cellRenderer={(rowIndex) => (
              <Cell>{data.recentStudents[rowIndex].email}</Cell>
            )}
          />
          <Column
            name="Total Sessions"
            cellRenderer={(rowIndex) => (
              <Cell>{data.recentStudents[rowIndex].total_sessions}</Cell>
            )}
          />
        </Table2>
      </Section>

      <Section
        title="Top Lecturers"
        elevation={1}
        collapsible={true}
        icon="people"
      >
        <HTMLTable>
          <thead>
            <tr>
              <th>Lecturer ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Courses Count</th>
            </tr>
          </thead>
          <tbody>
            {data.topLecturers.map((lecturer) => (
              <tr key={lecturer.lecturer_id}>
                <td>{lecturer.lecturer_id}</td>
                <td>{lecturer.name}</td>
                <td>{lecturer.email}</td>
                <td>{lecturer.courses_count}</td>
              </tr>
            ))}
          </tbody>
        </HTMLTable>
      </Section>

      <Section
        title="Popular Courses"
        elevation={1}
        collapsible={true}
        icon="book"
      >
        <HTMLTable>
          <thead>
            <tr>
              <th>Course ID</th>
              <th>Course Name</th>
              <th>Lecturer</th>
              <th>Students Count</th>
            </tr>
          </thead>
          <tbody>
            {data.popularCourses.map((course) => (
              <tr key={course.course_id}>
                <td>{course.course_id}</td>
                <td>{course.course_name}</td>
                <td>{course.lecturer_name}</td>
                <td>{course.students_count}</td>
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

      <Section
        title="Course Distribution"
        elevation={1}
        collapsible={true}
        className=" h-[300px]"
        icon="pie-chart"
      >
        {/* <Doughnut data={data.courseDistribution} /> */}
        {/* <Doughnut data={data.courseDistribution} /> */}
        <Doughnut
          data={data.courseDistribution}
          options={{
            responsive: true,
            maintainAspectRatio: false,
          }}
        />
      </Section>
      <Section title="Admin Actions" elevation={1}>
        <SectionCard className=" gap-1 flex">
          <Button
            intent={Intent.PRIMARY}
            text="Add Lecturer"
            onClick={() => setIsAddLecturerOpen(true)}
          />
          <Button
            intent={Intent.PRIMARY}
            text="Add Course"
            onClick={() => setIsAddCourseOpen(true)}
          />
          <Button
            intent={Intent.PRIMARY}
            text="Add Timetable Entry"
            onClick={() => setIsAddTimetableOpen(true)}
          />
        </SectionCard>
      </Section>

      {/* Updated Dialog components */}
      <Dialog
        isOpen={isAddLecturerOpen}
        onClose={() => setIsAddLecturerOpen(false)}
        title="Add Lecturer"
        icon="add"
      >
        <DialogBody>
          <FormGroup label="Name" labelFor="lecturer-name">
            <InputGroup id="lecturer-name" placeholder="Enter lecturer name" />
          </FormGroup>
          <FormGroup label="Email" labelFor="lecturer-email">
            <InputGroup
              id="lecturer-email"
              placeholder="Enter lecturer email"
            />
          </FormGroup>
          <FormGroup label="Password" labelFor="lecturer-password">
            <InputGroup
              id="lecturer-password"
              type="password"
              placeholder="Enter password"
            />
          </FormGroup>
        </DialogBody>
        <DialogFooter
          actions={
            <>
              <Button
                text="Cancel"
                onClick={() => setIsAddLecturerOpen(false)}
              />
              <Button
                intent={Intent.PRIMARY}
                text="Add Lecturer"
                onClick={() => {
                  const name = (
                    document.getElementById("lecturer-name") as HTMLInputElement
                  ).value;
                  const email = (
                    document.getElementById(
                      "lecturer-email"
                    ) as HTMLInputElement
                  ).value;
                  const password = (
                    document.getElementById(
                      "lecturer-password"
                    ) as HTMLInputElement
                  ).value;
                  handleAddLecturer(name, email, password);
                }}
              />
            </>
          }
        />
      </Dialog>

      <Dialog
        isOpen={isAddCourseOpen}
        onClose={() => setIsAddCourseOpen(false)}
        title="Add Course"
        icon="book"
      >
        <DialogBody>
          <FormGroup label="Course Name" labelFor="course-name">
            <InputGroup id="course-name" placeholder="Enter course name" />
          </FormGroup>
          <FormGroup label="Lecturer ID" labelFor="lecturer-id">
            <InputGroup id="lecturer-id" placeholder="Enter lecturer ID" />
          </FormGroup>
        </DialogBody>
        <DialogFooter
          actions={
            <>
              <Button text="Cancel" onClick={() => setIsAddCourseOpen(false)} />
              <Button
                intent={Intent.PRIMARY}
                text="Add Course"
                onClick={() => {
                  const courseName = (
                    document.getElementById("course-name") as HTMLInputElement
                  ).value;
                  const lecturerId = (
                    document.getElementById("lecturer-id") as HTMLInputElement
                  ).value;
                  handleAddCourse(courseName, lecturerId);
                }}
              />
            </>
          }
        />
      </Dialog>

      <Dialog
        isOpen={isAddTimetableOpen}
        onClose={() => setIsAddTimetableOpen(false)}
        title="Add Timetable Entry"
        icon="calendar"
      >
        <DialogBody>
          <FormGroup label="Course ID" labelFor="timetable-course-id">
            <InputGroup
              id="timetable-course-id"
              placeholder="Enter course ID"
            />
          </FormGroup>
          <FormGroup label="Day" labelFor="timetable-day">
            <InputGroup
              id="timetable-day"
              placeholder="Enter day (e.g., Monday)"
            />
          </FormGroup>
          <FormGroup label="Start Time" labelFor="timetable-start-time">
            <InputGroup
              id="timetable-start-time"
              placeholder="Enter start time (HH:MM)"
            />
          </FormGroup>
          <FormGroup label="End Time" labelFor="timetable-end-time">
            <InputGroup
              id="timetable-end-time"
              placeholder="Enter end time (HH:MM)"
            />
          </FormGroup>
        </DialogBody>
        <DialogFooter
          actions={
            <>
              <Button
                text="Cancel"
                onClick={() => setIsAddTimetableOpen(false)}
              />
              <Button
                intent={Intent.PRIMARY}
                text="Add Timetable Entry"
                onClick={() => {
                  const courseId = (
                    document.getElementById(
                      "timetable-course-id"
                    ) as HTMLInputElement
                  ).value;
                  const day = (
                    document.getElementById("timetable-day") as HTMLInputElement
                  ).value;
                  const startTime = (
                    document.getElementById(
                      "timetable-start-time"
                    ) as HTMLInputElement
                  ).value;
                  const endTime = (
                    document.getElementById(
                      "timetable-end-time"
                    ) as HTMLInputElement
                  ).value;
                  handleAddTimetable(courseId, day, startTime, endTime);
                }}
              />
            </>
          }
        />
      </Dialog>
    </div>
  );
};

export default AdminDashboard;

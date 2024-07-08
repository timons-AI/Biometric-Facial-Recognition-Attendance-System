import React from "react";
import { Card, H2 } from "@blueprintjs/core";
import StudentList from "../components/StudentList";
import TimetableComponent from "../components/Timetable";
import StudentRegistrationForm, {
  Student,
} from "../components/StudentRegistration";
import VideoFeed from "../components/Video";
import FaceRecognition from "../components/Attendance";
// import FaceRecognition from "../components/FaceRecognition";

const DashboardPage: React.FC = () => {
  const handleSubmit = (studentData: Student) => {
    console.log("Student data submitted:", studentData);
    // Handle form submission (e.g., send data to server)
  };
  return (
    <Card>
      <H2>Dashboard</H2>
      {/* <StudentRegistrationForm /> */}
      {/* <StudentRegistrationForm onSubmit={handleSubmit} /> */}
      <StudentList />
      <FaceRecognition />
      {/* <TimetableComponent /> */}
      {/* <VideoFeed /> */}
    </Card>
  );
};

export default DashboardPage;

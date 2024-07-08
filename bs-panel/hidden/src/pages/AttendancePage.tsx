import React from "react";
import { Card, H2 } from "@blueprintjs/core";
import AttendanceList from "../components/AttendanceList";
import TimetableComponent from "../components/Timetable";

const AttendancePage: React.FC = () => {
  return (
    <Card>
      <TimetableComponent />

      <AttendanceList />
    </Card>
  );
};

export default AttendancePage;

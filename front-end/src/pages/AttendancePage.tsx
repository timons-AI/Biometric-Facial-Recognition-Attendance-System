import React from "react";
import { Card, H2 } from "@blueprintjs/core";
import AttendanceList from "../components/AttendanceList";

const AttendancePage: React.FC = () => {
  return (
    <Card>
      <H2>Attendance Records</H2>
      <AttendanceList />
    </Card>
  );
};

export default AttendancePage;

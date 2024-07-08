import React from "react";
import { Card, H2 } from "@blueprintjs/core";
import StudentList from "../components/StudentList";

const DashboardPage: React.FC = () => {
  return (
    <Card>
      <H2>Dashboard</H2>
      <StudentList />
    </Card>
  );
};

export default DashboardPage;

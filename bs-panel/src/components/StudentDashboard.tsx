import React from "react";
import { Card, Callout, H3, H5, Tag } from "@blueprintjs/core";
import { useAtom } from "jotai";
import { userAtom } from "../store/auth";

const StudentDashboard: React.FC = () => {
  const [user] = useAtom(userAtom);

  return (
    <div className="p-4">
      <Callout intent="warning" title="Under Development">
        This dashboard is currently under development. More features will be
        added soon.
      </Callout>
      <Card className="mt-4">
        <H3>Welcome, {user?.name}</H3>
        <H5>Student Information</H5>
        <p>Email: {user?.email}</p>
        <p>
          Role: <Tag intent="primary">{user?.role}</Tag>
        </p>
        {/* Add more student-specific information here */}
      </Card>
    </div>
  );
};

export default StudentDashboard;

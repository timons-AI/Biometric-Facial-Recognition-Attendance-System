import React from "react";
import { Card, Callout, H3, Button } from "@blueprintjs/core";

const StudentViewPortal: React.FC = () => {
  return (
    <div className="p-4">
      <Callout intent="warning" title="Under Development">
        This portal is a placeholder for the IoT device interface. It will be
        used to capture student attendance.
      </Callout>
      <Card className="mt-4">
        <H3>Student Attendance Portal</H3>
        <p>This page will contain:</p>
        <ul>
          <li>A camera feed for facial recognition</li>
          <li>Real-time attendance status updates</li>
          <li>Quick check-in/check-out options</li>
        </ul>
        <Button intent="primary" text="Simulate Check-In" className="mr-2" />
        <Button intent="danger" text="Simulate Check-Out" />
      </Card>
    </div>
  );
};

export default StudentViewPortal;

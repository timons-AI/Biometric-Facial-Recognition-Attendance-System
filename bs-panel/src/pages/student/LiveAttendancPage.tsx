// src/pages/LiveAttendancePage.tsx

import React, { useEffect, useRef } from "react";
import { Callout, Card } from "@blueprintjs/core";

const LiveAttendancePage: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    // Set up WebSocket connection to receive live attendance data
    const ws = new WebSocket("ws://your-backend-url/live-attendance");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Update UI with received data
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div>
      <h2>Live Attendance</h2>
      <Callout intent="warning" className=" m-2">
        This page will be renderd on tablet screen at entrance of buildings to
        automatically register attendance, and give feedback in the future.
      </Callout>
      <Card>
        <video ref={videoRef} autoPlay muted />
        {/* Display attendance information here */}
      </Card>
    </div>
  );
};

export default LiveAttendancePage;

import React, { useEffect, useState } from "react";
import { HTMLTable } from "@blueprintjs/core";
import { getAttendance } from "../services/api";
import { AttendanceRecord } from "../types";

const AttendanceList: React.FC = () => {
  const [attendanceRecords, setAttendanceRecords] = useState<
    AttendanceRecord[]
  >([]);

  useEffect(() => {
    const fetchAttendance = async () => {
      const records = await getAttendance();
      setAttendanceRecords(records);
    };
    fetchAttendance();
  }, []);

  return (
    <HTMLTable>
      <thead>
        <tr>
          <th>Student ID</th>
          <th>Check-in Time</th>
        </tr>
      </thead>
      <tbody>
        {attendanceRecords.map((record, index) => (
          <tr key={index}>
            <td>{record.student_id}</td>
            <td>{new Date(record.check_in).toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </HTMLTable>
  );
};

export default AttendanceList;

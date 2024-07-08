import React, { useEffect, useState } from "react";
import axios from "axios";
import { Cell, Column, Table2 } from "@blueprintjs/table";
import { Spinner, HTMLSelect, Tag, Card, Elevation } from "@blueprintjs/core";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/table/lib/css/table.css";

interface Session {
  id: number;
  student_id: string;
  start_time: string;
  end_time: string | null;
  class_id: number;
}

interface Student {
  student_id: string;
  name: string;
}

interface SessionWithStudent extends Session {
  student_name: string;
}

const AttendanceList: React.FC = () => {
  const [sessions, setSessions] = useState<SessionWithStudent[]>([]);
  const [filteredSessions, setFilteredSessions] = useState<
    SessionWithStudent[]
  >([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [currentDay, setCurrentDay] = useState<string>(
    new Date().toLocaleDateString()
  );

  useEffect(() => {
    const fetchSessions = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [sessionsResponse, studentsResponse] = await Promise.all([
          axios.get<Session[]>("http://127.0.0.1:5000/api/sessions"),
          axios.get<Student[]>("http://127.0.0.1:5000/api/students"),
        ]);

        const sessionsWithStudents = sessionsResponse.data.map((session) => {
          const student = studentsResponse.data.find(
            (s) => s.student_id === session.student_id
          );
          return {
            ...session,
            student_name: student ? student.name : "Unknown",
          };
        });

        setSessions(sessionsWithStudents);
        filterSessionsByDay(sessionsWithStudents, currentDay);
      } catch (err) {
        setError("An error occurred while fetching session data");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchSessions();
  }, []);

  const filterSessionsByDay = (records: SessionWithStudent[], day: string) => {
    const filtered = records.filter(
      (record) => new Date(record.start_time).toLocaleDateString() === day
    );
    setFilteredSessions(filtered);
  };

  const handleDayChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedDay = event.target.value;
    setCurrentDay(selectedDay);
    filterSessionsByDay(sessions, selectedDay);
  };

  const cellRenderer = (rowIndex: number, columnIndex: number) => {
    const session = filteredSessions[rowIndex];
    switch (columnIndex) {
      case 0:
        return <Cell>{session.student_name}</Cell>;
      case 1:
        return <Cell>{session.student_id}</Cell>;
      case 2:
        return <Cell>{new Date(session.start_time).toLocaleTimeString()}</Cell>;
      case 3:
        return (
          <Cell>
            {session.end_time
              ? new Date(session.end_time).toLocaleTimeString()
              : "Ongoing"}
          </Cell>
        );
      case 4:
        return (
          <Cell
            className={`${
              session.end_time ? " bg-green-100 " : " bg-yellow-100"
            }`}
          >
            {/* <Tag
              minimal={true}
              intent={session.end_time ? "success" : "warning"}
            > */}
            {session.end_time ? "Completed" : "Ongoing"}
            {/* </Tag> */}
          </Cell>
        );
      default:
        return <Cell />;
    }
  };

  if (isLoading) return <Spinner />;
  if (error) return <div className="text-red-600">{error}</div>;

  const uniqueDays = [
    ...new Set(
      sessions.map((session) =>
        new Date(session.start_time).toLocaleDateString()
      )
    ),
  ];

  return (
    <div className="flex flex-col">
      <h2 className="text-2xl font-semibold mb-4">Attendance Sessions</h2>
      <div className="mb-4">
        <HTMLSelect value={currentDay} onChange={handleDayChange}>
          {uniqueDays.map((day) => (
            <option key={day} value={day}>
              {day}
            </option>
          ))}
        </HTMLSelect>
      </div>
      <div className="mb-4">
        <strong>Total Sessions:</strong>{" "}
        <Tag minimal={true} intent="primary">
          {filteredSessions.length}
        </Tag>
      </div>
      <div className="overflow-x-auto">
        <Table2
          numRows={filteredSessions.length}
          cellRendererDependencies={[filteredSessions]}
          className="min-w-full"
        >
          <Column
            name="Student Name"
            cellRenderer={(rowIndex) => cellRenderer(rowIndex, 0)}
          />
          <Column
            name="Student ID"
            cellRenderer={(rowIndex) => cellRenderer(rowIndex, 1)}
          />
          <Column
            name="Start Time"
            cellRenderer={(rowIndex) => cellRenderer(rowIndex, 2)}
          />
          <Column
            name="End Time"
            cellRenderer={(rowIndex) => cellRenderer(rowIndex, 3)}
          />
          <Column
            name="Status"
            cellRenderer={(rowIndex) => cellRenderer(rowIndex, 4)}
          />
        </Table2>
      </div>
      <div className="mt-8">
        <h3 className="text-xl font-semibold mb-4">
          Detailed Session Information
        </h3>
        {filteredSessions.map((session) => (
          <Card key={session.id} elevation={Elevation.TWO} className="mb-4">
            <h4>
              {session.student_name} ({session.student_id})
            </h4>
            <p>Start Time: {new Date(session.start_time).toLocaleString()}</p>
            <p>
              End Time:{" "}
              {session.end_time
                ? new Date(session.end_time).toLocaleString()
                : "Ongoing"}
            </p>
            <p>
              Duration:{" "}
              {session.end_time
                ? `${Math.round(
                    (new Date(session.end_time).getTime() -
                      new Date(session.start_time).getTime()) /
                      60000
                  )} minutes`
                : "Ongoing"}
            </p>
            <Tag intent={session.end_time ? "success" : "warning"}>
              {session.end_time ? "Completed" : "Ongoing"}
            </Tag>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default AttendanceList;

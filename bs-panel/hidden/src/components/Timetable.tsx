import React, { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@blueprintjs/core";
import { Cell, Column, Table2 } from "@blueprintjs/table";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/table/lib/css/table.css";

interface Lecturer {
  lecturer_id: number;
  first_name: string;
  last_name: string;
}

interface Class {
  class_id: number;
  class_name: string;
  lecturer_id: number;
}

interface TimetableEntry {
  timetable_id: number;
  class_id: number;
  day_of_week: string;
  start_time: string;
  end_time: string;
}

const TimetableComponent: React.FC = () => {
  const [lecturers, setLecturers] = useState<Lecturer[]>([]);
  const [classes, setClasses] = useState<Class[]>([]);
  const [timetable, setTimetable] = useState<TimetableEntry[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [lecturersRes, classesRes, timetableRes] = await Promise.all([
        axios.get<Lecturer[]>("http://127.0.0.1:5000/api/lecturers"),
        axios.get<Class[]>("http://127.0.0.1:5000/api/classes"),
        axios.get<TimetableEntry[]>("http://127.0.0.1:5000/api/timetable"),
      ]);

      setLecturers(lecturersRes.data);
      setClasses(classesRes.data);
      setTimetable(timetableRes.data);
    } catch (err) {
      setError("An error occurred while fetching data");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000); // Update every minute

    return () => clearInterval(timer);
  }, []);

  const generateSampleData = async () => {
    try {
      await axios.get("http://127.0.0.1:5000/populate");
      alert("Sample data generated successfully!");
      fetchData();
    } catch (err) {
      alert("An error occurred while generating sample data");
      console.error(err);
    }
  };

  if (isLoading) return <div className="text-center py-4">Loading...</div>;
  if (error)
    return <div className="text-center py-4 text-red-600">Error: {error}</div>;

  const getClassName = (classId: number) => {
    const classItem = classes.find((c) => c.class_id === classId);
    return classItem ? classItem.class_name : "Unknown";
  };

  const getLecturerName = (classId: number) => {
    const classItem = classes.find((c) => c.class_id === classId);
    if (!classItem) return "Unknown";
    const lecturer = lecturers.find(
      (l) => l.lecturer_id === classItem.lecturer_id
    );
    return lecturer
      ? `${lecturer.first_name} ${lecturer.last_name}`
      : "Unknown";
  };

  const isCurrentTimeSlot = (entry: TimetableEntry) => {
    const now = currentTime;
    const day = now.toLocaleString("en-US", { weekday: "long" });
    const time = now.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });

    return (
      entry.day_of_week === day &&
      entry.start_time <= time &&
      time < entry.end_time
    );
  };

  const HIGHLIGHTED_LECTURER_ID = 4; // Example: highlighting Margaret Nagwovuma's rows

  const isCurrentDay = (day: string) => {
    return currentTime.toLocaleString("en-US", { weekday: "long" }) === day;
  };

  const timetableCellRenderer = (rowIndex: number, columnIndex: number) => {
    const entry = timetable[rowIndex];
    const classItem = classes.find((c) => c.class_id === entry.class_id);
    const lecturer = lecturers.find(
      (l) => l.lecturer_id === classItem?.lecturer_id
    );

    const isCurrentSlot = isCurrentTimeSlot(entry);
    const isTodayRow = isCurrentDay(entry.day_of_week);
    const isHighlightedLecturer =
      lecturer?.lecturer_id === HIGHLIGHTED_LECTURER_ID;

    const cellStyle: React.CSSProperties = {
      backgroundColor: isCurrentSlot
        ? "#ecfccb"
        : isTodayRow
        ? "#f7fee7"
        : isHighlightedLecturer
        ? "#fff1f2"
        : undefined,
      fontWeight: isCurrentSlot ? "bold" : undefined,
    };

    const lecturerNameStyle: React.CSSProperties = isHighlightedLecturer
      ? {
          backgroundColor: "#ffe4e6",
          // padding: "2px 4px",s
        }
      : {};
    const combinedStyle = lecturerNameStyle
      ? { ...cellStyle, ...lecturerNameStyle }
      : cellStyle;

    switch (columnIndex) {
      case 0:
        return <Cell style={cellStyle}>{getClassName(entry.class_id)}</Cell>;
      case 1:
        return (
          <Cell style={combinedStyle}>{getLecturerName(entry.class_id)}</Cell>
        );
      case 2:
        return <Cell style={cellStyle}>{entry.day_of_week}</Cell>;
      case 3:
        return <Cell style={cellStyle}>{entry.start_time}</Cell>;
      case 4:
        return <Cell style={cellStyle}>{entry.end_time}</Cell>;
      default:
        return <Cell />;
    }
  };

  return (
    <div className="flex flex-col">
      <h2 className="text-2xl font-semibold mb-4">Timetable for Mercy Amiyo</h2>
      <div className="overflow-x-auto">
        <Table2
          numRows={timetable.length}
          cellRendererDependencies={[
            timetable,
            classes,
            lecturers,
            currentTime,
          ]}
          className="min-w-full"
        >
          <Column
            name="Class Name"
            cellRenderer={(rowIndex) => timetableCellRenderer(rowIndex, 0)}
          />
          <Column
            name="Lecturer"
            cellRenderer={(rowIndex) => timetableCellRenderer(rowIndex, 1)}
          />
          <Column
            name="Day"
            cellRenderer={(rowIndex) => timetableCellRenderer(rowIndex, 2)}
          />
          <Column
            name="Start Time"
            cellRenderer={(rowIndex) => timetableCellRenderer(rowIndex, 3)}
          />
          <Column
            name="End Time"
            cellRenderer={(rowIndex) => timetableCellRenderer(rowIndex, 4)}
          />
        </Table2>
      </div>
      {/* <Button onClick={generateSampleData} className="mt-4">
        Generate Sample Data
      </Button> */}
    </div>
  );
};

export default TimetableComponent;

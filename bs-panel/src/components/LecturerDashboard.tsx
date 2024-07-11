import React, { useState, useEffect } from "react";
import {
  Card,
  Elevation,
  H3,
  H4,
  H5,
  Tag,
  Button,
  Collapse,
} from "@blueprintjs/core";
import { useAtom } from "jotai";
import { userAtom } from "../store/auth";
import { Course, TimetableEntry } from "../timetable";
import api from "../api/api";

const daysOfWeek = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

const LecturerDashboard: React.FC = () => {
  const [user] = useAtom(userAtom);
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [currentDay] = useState<string>(daysOfWeek[new Date().getDay() - 1]);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await api.get("/lecturer/timetable");
        setCourses(response.data);
      } catch (error) {
        console.error("Error fetching timetable:", error);
      }
    };
    fetchCourses();
  }, []);

  const hasLectureToday = (course: Course) => {
    return course.timetableEntries.some((entry) => entry.day === currentDay);
  };

  return (
    <div className="p-4">
      <H3>Welcome, {user?.name}</H3>
      <H4>Your Courses</H4>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
        {courses.map((course) => (
          <Card
            key={course.id}
            elevation={Elevation.TWO}
            interactive={true}
            onClick={() => setSelectedCourse(course)}
          >
            <H5>{course.name}</H5>
            {hasLectureToday(course) && (
              <Tag intent="primary">Lecture Today</Tag>
            )}
          </Card>
        ))}
      </div>
      {selectedCourse && (
        <CourseDetail course={selectedCourse} currentDay={currentDay} />
      )}
    </div>
  );
};

interface CourseDetailProps {
  course: Course;
  currentDay: string;
}

const CourseDetail: React.FC<CourseDetailProps> = ({ course, currentDay }) => {
  return (
    <Card elevation={Elevation.TWO}>
      <H4>{course.name} Timetable</H4>
      <DayTimetable
        entries={course.timetableEntries.filter(
          (entry) => entry.day === currentDay
        )}
        day={currentDay}
        isOpen={true}
      />
      {daysOfWeek
        .filter((day) => day !== currentDay)
        .map((day) => (
          <DayTimetable
            key={day}
            entries={course.timetableEntries.filter(
              (entry) => entry.day === day
            )}
            day={day}
            isOpen={false}
          />
        ))}
    </Card>
  );
};

interface DayTimetableProps {
  entries: TimetableEntry[];
  day: string;
  isOpen: boolean;
}

const DayTimetable: React.FC<DayTimetableProps> = ({
  entries,
  day,
  isOpen,
}) => {
  const [isExpanded, setIsExpanded] = useState(isOpen);
  const isCurrentlyRunning = (entry: TimetableEntry) => {
    const now = new Date();
    const startTime = new Date();
    const endTime = new Date();
    const [startHour, startMinute] = entry.startTime.split(":");
    const [endHour, endMinute] = entry.endTime.split(":");
    startTime.setHours(parseInt(startHour), parseInt(startMinute));
    endTime.setHours(parseInt(endHour), parseInt(endMinute));
    return now >= startTime && now <= endTime;
  };
  return (
    <Card className="mb-2">
      <Button
        fill
        minimal
        rightIcon={isExpanded ? "chevron-up" : "chevron-down"}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <H5>{day}</H5>
      </Button>
      <Collapse isOpen={isExpanded}>
        {entries.length > 0 ? (
          entries.map((entry) => (
            <Card key={entry.id} className="mt-2">
              <p>Course Unit: {entry.courseUnit.name}</p>
              <p>
                Time: {entry.startTime} - {entry.endTime}
              </p>
              <p>Room: {entry.room}</p>
              {isCurrentlyRunning(entry) && (
                <Tag intent="success">Currently Running</Tag>
              )}
            </Card>
          ))
        ) : (
          <p>No lectures scheduled for this day.</p>
        )}
      </Collapse>
    </Card>
  );
};

export default LecturerDashboard;

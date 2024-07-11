import React, { useState, useEffect } from "react";
import {
  Card,
  FormGroup,
  InputGroup,
  Button,
  HTMLSelect,
  H3,
  H4,
  Intent,
  Toaster,
  Position,
  Callout,
} from "@blueprintjs/core";
import { useAtom } from "jotai";
import { userAtom } from "../store/auth";
import api from "../api/api";

const AppToaster = Toaster.create({
  className: "recipe-toaster",
  position: Position.TOP,
});

interface AcademicYear {
  id: number;
  year: string;
}

interface Semester {
  id: number;
  name: string;
  academicYearId: number;
}

interface College {
  id: number;
  name: string;
}

interface Course {
  id: number;
  name: string;
  collegeId: number;
}

interface CourseUnit {
  id: number;
  code: string;
  name: string;
  courseId: number;
}

interface Lecturer {
  id: number;
  name: string;
}

interface TimetableEntry {
  id?: number;
  semesterId: number;
  courseUnitId: number;
  day: string;
  startTime: string;
  endTime: string;
  room: string;
  lecturerId: number;
}

const daysOfWeek = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

const AdminTimetableManagement: React.FC = () => {
  const [user] = useAtom(userAtom);
  const [academicYears, setAcademicYears] = useState<AcademicYear[]>([]);
  const [semesters, setSemesters] = useState<Semester[]>([]);
  const [colleges, setColleges] = useState<College[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [courseUnits, setCourseUnits] = useState<CourseUnit[]>([]);
  const [lecturers, setLecturers] = useState<Lecturer[]>([]);

  const [newAcademicYear, setNewAcademicYear] = useState("");
  const [newSemester, setNewSemester] = useState({
    name: "",
    academicYearId: "",
  });
  const [newCollege, setNewCollege] = useState("");
  const [newCourse, setNewCourse] = useState({ name: "", collegeId: "" });
  const [newCourseUnit, setNewCourseUnit] = useState({
    code: "",
    name: "",
    courseId: "",
  });
  const [newTimetableEntry, setNewTimetableEntry] = useState<TimetableEntry>({
    semesterId: 0,
    courseUnitId: 0,
    day: "Monday",
    startTime: "",
    endTime: "",
    room: "",
    lecturerId: 0,
  });

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      const [
        yearsRes,
        semestersRes,
        collegesRes,
        coursesRes,
        unitsRes,
        lecturersRes,
      ] = await Promise.all([
        api.get("/admin/academic-years"),
        api.get("/admin/semesters"),
        api.get("/admin/colleges"),
        api.get("/admin/courses"),
        api.get("/admin/course-units"),
        api.get("/admin/lecturers"),
      ]);
      setAcademicYears(yearsRes.data);
      setSemesters(semestersRes.data);
      setColleges(collegesRes.data);
      setCourses(coursesRes.data);
      setCourseUnits(unitsRes.data);
      setLecturers(lecturersRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      AppToaster.show({
        message: "Error fetching data",
        intent: Intent.DANGER,
      });
    }
  };

  const handleCreateAcademicYear = async () => {
    try {
      await api.post("/admin/academic-years", { year: newAcademicYear });
      setNewAcademicYear("");
      fetchAllData();
      AppToaster.show({
        message: "Academic year created successfully",
        intent: Intent.SUCCESS,
      });
    } catch (error) {
      console.error("Error creating academic year:", error);
      AppToaster.show({
        message: "Error creating academic year",
        intent: Intent.DANGER,
      });
    }
  };

  const handleCreateSemester = async () => {
    try {
      await api.post("/admin/semesters", newSemester);
      setNewSemester({ name: "", academicYearId: "" });
      fetchAllData();
      AppToaster.show({
        message: "Semester created successfully",
        intent: Intent.SUCCESS,
      });
    } catch (error) {
      console.error("Error creating semester:", error);
      AppToaster.show({
        message: "Error creating semester",
        intent: Intent.DANGER,
      });
    }
  };

  const handleCreateCollege = async () => {
    try {
      await api.post("/admin/colleges", { name: newCollege });
      setNewCollege("");
      fetchAllData();
      AppToaster.show({
        message: "College created successfully",
        intent: Intent.SUCCESS,
      });
    } catch (error) {
      console.error("Error creating college:", error);
      AppToaster.show({
        message: "Error creating college",
        intent: Intent.DANGER,
      });
    }
  };

  const handleCreateCourse = async () => {
    try {
      await api.post("/admin/courses", newCourse);
      setNewCourse({ name: "", collegeId: "" });
      fetchAllData();
      AppToaster.show({
        message: "Course created successfully",
        intent: Intent.SUCCESS,
      });
    } catch (error) {
      console.error("Error creating course:", error);
      AppToaster.show({
        message: "Error creating course",
        intent: Intent.DANGER,
      });
    }
  };

  const handleCreateCourseUnit = async () => {
    try {
      await api.post("/admin/course-units", newCourseUnit);
      setNewCourseUnit({ code: "", name: "", courseId: "" });
      fetchAllData();
      AppToaster.show({
        message: "Course unit created successfully",
        intent: Intent.SUCCESS,
      });
    } catch (error) {
      console.error("Error creating course unit:", error);
      AppToaster.show({
        message: "Error creating course unit",
        intent: Intent.DANGER,
      });
    }
  };

  const handleCreateTimetableEntry = async () => {
    try {
      await api.post("/admin/timetable-entries", newTimetableEntry);
      setNewTimetableEntry({
        semesterId: 0,
        courseUnitId: 0,
        day: "Monday",
        startTime: "",
        endTime: "",
        room: "",
        lecturerId: 0,
      });
      fetchAllData();
      AppToaster.show({
        message: "Timetable entry created successfully",
        intent: Intent.SUCCESS,
      });
    } catch (error) {
      console.error("Error creating timetable entry:", error);
      AppToaster.show({
        message: "Error creating timetable entry",
        intent: Intent.DANGER,
      });
    }
  };

  return (
    <div className="p-4">
      <Callout intent="warning" title="Under Development" className=" my-2">
        This dashboard is currently under development. More features will be
        added soon.
      </Callout>
      <H3>Timetable Management</H3>

      <Card className="mb-4">
        <H4>Create Academic Year</H4>
        <FormGroup label="Academic Year" labelFor="academic-year-input">
          <InputGroup
            id="academic-year-input"
            value={newAcademicYear}
            onChange={(e) => setNewAcademicYear(e.target.value)}
            placeholder="e.g., 2023/2024"
          />
        </FormGroup>
        <Button intent={Intent.PRIMARY} onClick={handleCreateAcademicYear}>
          Create Academic Year
        </Button>
      </Card>

      <Card className="mb-4">
        <H4>Create Semester</H4>
        <FormGroup label="Semester Name" labelFor="semester-name-input">
          <InputGroup
            id="semester-name-input"
            value={newSemester.name}
            onChange={(e) =>
              setNewSemester({ ...newSemester, name: e.target.value })
            }
            placeholder="e.g., Semester I"
          />
        </FormGroup>
        <FormGroup label="Academic Year" labelFor="semester-year-select">
          <HTMLSelect
            id="semester-year-select"
            value={newSemester.academicYearId}
            onChange={(e) =>
              setNewSemester({ ...newSemester, academicYearId: e.target.value })
            }
          >
            <option value="">Select Academic Year</option>
            {academicYears.map((year) => (
              <option key={year.id} value={year.id}>
                {year.year}
              </option>
            ))}
          </HTMLSelect>
        </FormGroup>
        <Button intent={Intent.PRIMARY} onClick={handleCreateSemester}>
          Create Semester
        </Button>
      </Card>

      <Card className="mb-4">
        <H4>Create College</H4>
        <FormGroup label="College Name" labelFor="college-name-input">
          <InputGroup
            id="college-name-input"
            value={newCollege}
            onChange={(e) => setNewCollege(e.target.value)}
            placeholder="e.g., College of Computing and Information Sciences"
          />
        </FormGroup>
        <Button intent={Intent.PRIMARY} onClick={handleCreateCollege}>
          Create College
        </Button>
      </Card>

      <Card className="mb-4">
        <H4>Create Course</H4>
        <FormGroup label="Course Name" labelFor="course-name-input">
          <InputGroup
            id="course-name-input"
            value={newCourse.name}
            onChange={(e) =>
              setNewCourse({ ...newCourse, name: e.target.value })
            }
            placeholder="e.g., Computer Science"
          />
        </FormGroup>
        <FormGroup label="College" labelFor="course-college-select">
          <HTMLSelect
            id="course-college-select"
            value={newCourse.collegeId}
            onChange={(e) =>
              setNewCourse({ ...newCourse, collegeId: e.target.value })
            }
          >
            <option value="">Select College</option>
            {colleges.map((college) => (
              <option key={college.id} value={college.id}>
                {college.name}
              </option>
            ))}
          </HTMLSelect>
        </FormGroup>
        <Button intent={Intent.PRIMARY} onClick={handleCreateCourse}>
          Create Course
        </Button>
      </Card>

      <Card className="mb-4">
        <H4>Create Course Unit</H4>
        <FormGroup label="Course Unit Code" labelFor="course-unit-code-input">
          <InputGroup
            id="course-unit-code-input"
            value={newCourseUnit.code}
            onChange={(e) =>
              setNewCourseUnit({ ...newCourseUnit, code: e.target.value })
            }
            placeholder="e.g., CS101"
          />
        </FormGroup>
        <FormGroup label="Course Unit Name" labelFor="course-unit-name-input">
          <InputGroup
            id="course-unit-name-input"
            value={newCourseUnit.name}
            onChange={(e) =>
              setNewCourseUnit({ ...newCourseUnit, name: e.target.value })
            }
            placeholder="e.g., Introduction to Programming"
          />
        </FormGroup>
        <FormGroup label="Course" labelFor="course-unit-course-select">
          <HTMLSelect
            id="course-unit-course-select"
            value={newCourseUnit.courseId}
            onChange={(e) =>
              setNewCourseUnit({ ...newCourseUnit, courseId: e.target.value })
            }
          >
            <option value="">Select Course</option>
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.name}
              </option>
            ))}
          </HTMLSelect>
        </FormGroup>
        <Button intent={Intent.PRIMARY} onClick={handleCreateCourseUnit}>
          Create Course Unit
        </Button>
      </Card>

      <Card className="mb-4">
        <H4>Create Timetable Entry</H4>
        <FormGroup label="Semester" labelFor="timetable-semester-select">
          <HTMLSelect
            id="timetable-semester-select"
            value={newTimetableEntry.semesterId}
            onChange={(e) =>
              setNewTimetableEntry({
                ...newTimetableEntry,
                semesterId: Number(e.target.value),
              })
            }
          >
            <option value="">Select Semester</option>
            {semesters.map((semester) => (
              <option key={semester.id} value={semester.id}>
                {semester.name}
              </option>
            ))}
          </HTMLSelect>
        </FormGroup>
        <FormGroup label="Course Unit" labelFor="timetable-course-unit-select">
          <HTMLSelect
            id="timetable-course-unit-select"
            value={newTimetableEntry.courseUnitId}
            onChange={(e) =>
              setNewTimetableEntry({
                ...newTimetableEntry,
                courseUnitId: Number(e.target.value),
              })
            }
          >
            <option value="">Select Course Unit</option>
            {courseUnits.map((unit) => (
              <option key={unit.id} value={unit.id}>
                {unit.code} - {unit.name}
              </option>
            ))}
          </HTMLSelect>
        </FormGroup>
        <FormGroup label="Day" labelFor="timetable-day-select">
          <HTMLSelect
            id="timetable-day-select"
            value={newTimetableEntry.day}
            onChange={(e) =>
              setNewTimetableEntry({
                ...newTimetableEntry,
                day: e.target.value,
              })
            }
          >
            {daysOfWeek.map((day) => (
              <option key={day} value={day}>
                {day}
              </option>
            ))}
          </HTMLSelect>
        </FormGroup>
        <FormGroup label="Start Time" labelFor="timetable-start-time-input">
          <InputGroup
            id="timetable-start-time-input"
            type="time"
            value={newTimetableEntry.startTime}
            onChange={(e) =>
              setNewTimetableEntry({
                ...newTimetableEntry,
                startTime: e.target.value,
              })
            }
          />
        </FormGroup>
        <FormGroup label="End Time" labelFor="timetable-end-time-input">
          <InputGroup
            id="timetable-end-time-input"
            type="time"
            value={newTimetableEntry.endTime}
            onChange={(e) =>
              setNewTimetableEntry({
                ...newTimetableEntry,
                endTime: e.target.value,
              })
            }
          />
        </FormGroup>
        <FormGroup label="Room" labelFor="timetable-room-input">
          <InputGroup
            id="timetable-room-input"
            value={newTimetableEntry.room}
            onChange={(e) =>
              setNewTimetableEntry({
                ...newTimetableEntry,
                room: e.target.value,
              })
            }
            placeholder="e.g., Room 101"
          />
        </FormGroup>
        <FormGroup label="Lecturer" labelFor="timetable-lecturer-select">
          <HTMLSelect
            id="timetable-lecturer-select"
            value={newTimetableEntry.lecturerId}
            onChange={(e) =>
              setNewTimetableEntry({
                ...newTimetableEntry,
                lecturerId: Number(e.target.value),
              })
            }
          >
            <option value="">Select Lecturer</option>
            {lecturers.map((lecturer) => (
              <option key={lecturer.id} value={lecturer.id}>
                {lecturer.name}
              </option>
            ))}
          </HTMLSelect>
        </FormGroup>
        <Button intent={Intent.PRIMARY} onClick={handleCreateTimetableEntry}>
          Create Timetable Entry
        </Button>
      </Card>
    </div>
  );
};

export default AdminTimetableManagement;

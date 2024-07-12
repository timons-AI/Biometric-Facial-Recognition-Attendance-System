import React, { useState, useEffect } from "react";
import {
  Card,
  FormGroup,
  InputGroup,
  Button,
  HTMLSelect,
  Intent,
} from "@blueprintjs/core";
import api, { register } from "../api/api";
import FaceCapture from "./FaceCapture";
import { showToast } from "./Toaster";

interface AcademicYear {
  id: number;
  year: string;
}

interface Semester {
  id: number;
  name: string;
}

interface College {
  id: number;
  name: string;
}

interface Course {
  id: number;
  code: string;
  name: string;
}

const RegistrationForm: React.FC = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    academic_year_id: "",
    semester_id: "",
    college_id: "",
    course_id: "",
    student_id: "",
    role: "student",
  });
  const [academicYears, setAcademicYears] = useState<AcademicYear[]>([]);
  const [semesters, setSemesters] = useState<Semester[]>([]);
  const [colleges, setColleges] = useState<College[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);

  useEffect(() => {
    fetchOptions();
  }, []);

  const fetchOptions = async () => {
    try {
      const [yearsRes, semestersRes, collegesRes, coursesRes] =
        await Promise.all([
          api.get("/academic-years"),
          api.get("/semesters"),
          api.get("/colleges"),
          api.get("/courses"),
        ]);
      setAcademicYears(yearsRes.data);
      setSemesters(semestersRes.data);
      setColleges(collegesRes.data);
      setCourses(coursesRes.data);
    } catch (error) {
      console.error("Error fetching options:", error);
      showToast("Error fetching options", Intent.DANGER);
    }
  };

  const [faceImages, setFaceImages] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = event.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const userData = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        userData.append(key, value.toString());
      });
      faceImages.forEach((image, index) => {
        userData.append(`faceImage${index}`, image);
      });

      console.log("Sending data:", Object.fromEntries(userData));

      await register(userData);

      showToast("Registration successful. Please login.", Intent.SUCCESS);
    } catch (error) {
      console.error("Registration failed:", error);
      showToast("Registration failed. Please try again later.", Intent.DANGER);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card elevation={2} className="registration-form">
      <h2>Student Registration</h2>
      <form onSubmit={handleSubmit}>
        <FormGroup label="Name" labelFor="name-input">
          <InputGroup
            id="name-input"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
          />
        </FormGroup>
        <FormGroup label="Email" labelFor="email-input">
          <InputGroup
            id="email-input"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleInputChange}
            required
          />
        </FormGroup>
        <FormGroup label="Password" labelFor="password-input">
          <InputGroup
            id="password-input"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleInputChange}
            required
          />
        </FormGroup>
        <FormGroup label="Student ID" labelFor="studentId-input">
          <InputGroup
            id="studentId-input"
            name="student_id"
            value={formData.student_id}
            onChange={handleInputChange}
            required
          />
        </FormGroup>
        <FormGroup label="Academic Year" labelFor="academicYear-select">
          <HTMLSelect
            id="academicYear-select"
            name="academic_year_id"
            value={formData.academic_year_id}
            onChange={handleInputChange}
            required
          >
            <option value="">Select Academic Year</option>
            {academicYears.map((year) => (
              <option key={year.id} value={year.id}>
                {year.year}
              </option>
            ))}
          </HTMLSelect>
        </FormGroup>
        <FormGroup label="Semester" labelFor="semester-select">
          <HTMLSelect
            id="semester-select"
            name="semester_id"
            value={formData.semester_id}
            onChange={handleInputChange}
            required
          >
            <option value="">Select Semester</option>
            {semesters.map((semester) => (
              <option key={semester.id} value={semester.id}>
                {semester.name}
              </option>
            ))}
          </HTMLSelect>
        </FormGroup>
        <FormGroup label="College" labelFor="college-select">
          <HTMLSelect
            id="college-select"
            name="college_id"
            value={formData.college_id}
            onChange={handleInputChange}
            required
          >
            <option value="">Select College</option>
            {colleges.map((college) => (
              <option key={college.id} value={college.id}>
                {college.name}
              </option>
            ))}
          </HTMLSelect>
        </FormGroup>
        <FormGroup label="Course" labelFor="course-select">
          <HTMLSelect
            id="course-select"
            name="course_id"
            value={formData.course_id}
            onChange={handleInputChange}
            required
          >
            <option value="">Select Course</option>
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.code} - {course.name}
              </option>
            ))}
          </HTMLSelect>
        </FormGroup>
        <FormGroup label="Capture Image" labelFor="image-capture">
          <FaceCapture onCapture={setFaceImages} />
        </FormGroup>
        <Button
          type="submit"
          intent={Intent.PRIMARY}
          text="Register"
          className="w-full mt-4"
          loading={isLoading}
        />
      </form>
    </Card>
  );
};

export default RegistrationForm;

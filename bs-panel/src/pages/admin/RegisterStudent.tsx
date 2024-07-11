import React, { useState } from "react";
import {
  Card,
  Button,
  Intent,
  Callout,
  FormGroup,
  InputGroup,
  HTMLSelect,
} from "@blueprintjs/core";
import { registerStudent } from "../../services/api";
import FaceCapture from "../../components/FaceCapture";

interface Student {
  student_id: string;
  name: string;
  email: string;
  password: string;
}

const RegisterStudentPage: React.FC = () => {
  const [studentData, setStudentData] = useState<Student>({
    student_id: "",
    name: "",
    email: "",
    password: "",
  });
  const [images, setImages] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [academicYear, setAcademicYear] = useState("");
  const [college, setCollege] = useState("");
  const [group, setGroup] = useState("");
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setStudentData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError(null);
    // setLoading(true);

    if (images.length < 1) {
      setError("Please capture at least one image of the student.");
      return;
    }

    if (!studentData.password) {
      setError("Please enter a password for the student.");
      return;
    }

    try {
      setLoading(true);
      await registerStudent(studentData, images);
      setStudentData({ student_id: "", name: "", email: "", password: "" });
      setImages([]);
      setLoading(false);
      alert("Student registered successfully!");
    } catch (error: any) {
      setLoading(false);
      setError(
        error.response?.data?.error ||
          "Failed to register student. Please try again."
      );
    }
  };

  return (
    <Card className=" w-2/3 m-2">
      <h2>Register New Student</h2>
      {error && <Callout intent={Intent.DANGER}>{error}</Callout>}
      <Callout className=" m-2" intent={Intent.WARNING}>
        Timetable assignment is currently under construction. The following
        fields will be used for automatic timetable assignment in the future.
      </Callout>
      <form onSubmit={handleSubmit}>
        <FormGroup
          label="Student ID"
          labelFor="student_id-input"
          labelInfo="(required)"
        >
          <InputGroup
            leftIcon="id-number"
            id="student_id-input"
            name="student_id"
            placeholder="Enter student ID"
            value={studentData.student_id}
            onChange={handleInputChange}
            required
          />
        </FormGroup>
        <FormGroup label="Name" labelFor="name-input" labelInfo="(required)">
          <InputGroup
            leftIcon="user"
            id="name-input"
            name="name"
            placeholder="Enter full name"
            value={studentData.name}
            onChange={handleInputChange}
            required
          />
        </FormGroup>
        <FormGroup label="Email" labelFor="email-input" labelInfo="(required)">
          <InputGroup
            leftIcon="envelope"
            id="email-input"
            name="email"
            placeholder="Enter email address"
            value={studentData.email}
            onChange={handleInputChange}
            type="email"
            required
          />
        </FormGroup>
        <FormGroup
          label="Password"
          labelFor="password-input"
          labelInfo="(required)"
        >
          <InputGroup
            leftIcon="lock"
            id="password-input"
            name="password"
            placeholder="Enter password"
            value={studentData.password}
            onChange={handleInputChange}
            type="password"
            required
          />
        </FormGroup>
        <FormGroup label="Student Image" labelFor="image-capture">
          <FaceCapture onCapture={setImages} />
        </FormGroup>
        <FormGroup label="Academic Year" labelFor="academic-year-input">
          <HTMLSelect
            id="academic-year-input"
            value={academicYear}
            onChange={(e) => setAcademicYear(e.target.value)}
            disabled
          >
            <option value="">Select Academic Year</option>
            <option value="1">First Year</option>
            <option value="2">Second Year</option>
            <option value="3">Third Year</option>
            <option value="4">Fourth Year</option>
          </HTMLSelect>
        </FormGroup>
        <FormGroup label="College" labelFor="college-input">
          <HTMLSelect
            id="college-input"
            value={college}
            onChange={(e) => setCollege(e.target.value)}
            disabled
          >
            <option value="">Select College</option>
            <option value="engineering">College of Engineering</option>
            <option value="science">College of Science</option>
            <option value="business">College of Business</option>
          </HTMLSelect>
        </FormGroup>
        <FormGroup label="Group" labelFor="group-input">
          <HTMLSelect
            id="group-input"
            value={group}
            onChange={(e) => setGroup(e.target.value)}
            disabled
          >
            <option value="">Select Group</option>
            <option value="A">Group A</option>
            <option value="B">Group B</option>
            <option value="C">Group C</option>
          </HTMLSelect>
        </FormGroup>
        <Button
          type="submit"
          intent={Intent.PRIMARY}
          loading={loading}
          text="Register Student"
          disabled={
            !studentData.student_id ||
            !studentData.name ||
            !studentData.email ||
            images.length < 1
          }
        />
      </form>
    </Card>
  );
};

export default RegisterStudentPage;

import React, { useState } from "react";
import {
  Card,
  Button,
  Intent,
  Callout,
  FormGroup,
  InputGroup,
  MenuItem,
} from "@blueprintjs/core";
import { Select } from "@blueprintjs/select";
import { registerStudent } from "../services/api";
import FaceCapture from "../components/FaceCapture";

interface Student {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  studentId: string;
  academicYear: number;
  semester: "sem 1" | "sem 2";
  academicType: "teaching" | "tests" | "examination" | "recess term";
  academicGroup: string;
}

const academicYears = [2024, 2025, 2026, 2027];
const semesters: Array<"sem 1" | "sem 2"> = ["sem 1", "sem 2"];
const academicTypes: Array<
  "teaching" | "tests" | "examination" | "recess term"
> = ["teaching", "tests", "examination", "recess term"];
const academicGroups = ["Group A", "Group B", "Group C", "Group D"];

const RegisterPage: React.FC = () => {
  const [studentData, setStudentData] = useState<Student>({
    firstName: "",
    lastName: "",
    email: "",
    studentId: "",
    password: "",
    academicYear: 2024,
    semester: "sem 1",
    academicType: "teaching",
    academicGroup: "Group A",
  });
  const [images, setImages] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setStudentData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSelectChange = (field: keyof Student) => (value: any) => {
    setStudentData((prevData) => ({
      ...prevData,
      [field]: value,
    }));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (images.length < 5) {
      setError("Please capture at least 5 images of the student.");
      return;
    }

    console.log(`Submitting ${images.length} images`);

    try {
      await registerStudent(studentData, images);
      setStudentData({
        firstName: "",
        lastName: "",
        email: "",
        password: "",
        studentId: "",
        academicYear: 2024,
        semester: "sem 1",
        academicType: "teaching",
        academicGroup: "Group A",
      });
      setImages([]);
      alert("Student registered successfully!");
    } catch (error: any) {
      if (error.response && error.response.data && error.response.data.error) {
        setError(error.response.data.error);
      } else {
        setError("Failed to register student. Please try again.");
      }
    }
  };

  const renderSelectItem = (item: any, { handleClick }: any) => (
    <MenuItem text={item} onClick={handleClick} roleStructure="listoption" />
  );

  return (
    <Card className="grid gap-2">
      <h2>Register New Student</h2>
      {error && <Callout intent={Intent.DANGER}>{error}</Callout>}
      <form onSubmit={handleSubmit}>
        <FormGroup
          label="First Name"
          labelFor="firstName-input"
          labelInfo="(required)"
        >
          <InputGroup
            id="firstName-input"
            name="firstName"
            placeholder="Enter first name"
            value={studentData.firstName}
            onChange={handleInputChange}
            intent={Intent.PRIMARY}
          />
        </FormGroup>
        <FormGroup
          label="Last Name"
          labelFor="lastName-input"
          labelInfo="(required)"
        >
          <InputGroup
            id="lastName-input"
            name="lastName"
            placeholder="Enter last name"
            value={studentData.lastName}
            onChange={handleInputChange}
            intent={Intent.PRIMARY}
          />
        </FormGroup>
        <FormGroup
          label="Student ID"
          labelFor="studentId-input"
          labelInfo="(required)"
        >
          <InputGroup
            id="studentId-input"
            name="studentId"
            placeholder="Enter student ID"
            value={studentData.studentId}
            onChange={handleInputChange}
            intent={Intent.PRIMARY}
          />
        </FormGroup>
        <FormGroup label="Email" labelFor="email-input" labelInfo="(required)">
          <InputGroup
            id="email-input"
            name="email"
            placeholder="Enter email address"
            value={studentData.email}
            onChange={handleInputChange}
            intent={Intent.PRIMARY}
            type="email"
          />
        </FormGroup>
        <FormGroup
          label="Password"
          labelFor="password-input"
          labelInfo="(required)"
        >
          <InputGroup
            id="password-input"
            name="password"
            placeholder="Enter password"
            value={studentData.password}
            onChange={handleInputChange}
            intent={Intent.PRIMARY}
            type="password"
          />
        </FormGroup>
        <FormGroup label="Academic Year" labelFor="academicYear-select">
          <Select
            items={academicYears}
            itemRenderer={renderSelectItem}
            onItemSelect={handleSelectChange("academicYear")}
            filterable={false}
          >
            <Button
              text={studentData.academicYear}
              rightIcon="double-caret-vertical"
            />
          </Select>
        </FormGroup>
        <FormGroup label="Semester" labelFor="semester-select">
          <Select
            items={semesters}
            itemRenderer={renderSelectItem}
            onItemSelect={handleSelectChange("semester")}
            filterable={false}
          >
            <Button
              text={studentData.semester}
              rightIcon="double-caret-vertical"
            />
          </Select>
        </FormGroup>
        <FormGroup label="Academic Type" labelFor="academicType-select">
          <Select
            items={academicTypes}
            itemRenderer={renderSelectItem}
            onItemSelect={handleSelectChange("academicType")}
            filterable={false}
          >
            <Button
              text={studentData.academicType}
              rightIcon="double-caret-vertical"
            />
          </Select>
        </FormGroup>
        <FormGroup label="Academic Group" labelFor="academicGroup-select">
          <Select
            items={academicGroups}
            itemRenderer={renderSelectItem}
            onItemSelect={handleSelectChange("academicGroup")}
            filterable={false}
          >
            <Button
              text={studentData.academicGroup}
              rightIcon="double-caret-vertical"
            />
          </Select>
        </FormGroup>
        <FormGroup label="Student Image" labelFor="image-capture">
          <FaceCapture onCapture={setImages} />
        </FormGroup>
        <Button
          type="submit"
          intent={Intent.PRIMARY}
          text="Register Student"
          disabled={
            !studentData.firstName ||
            !studentData.lastName ||
            !studentData.email ||
            !studentData.password ||
            images.length < 5
          }
        />
      </form>
    </Card>
  );
};

export default RegisterPage;

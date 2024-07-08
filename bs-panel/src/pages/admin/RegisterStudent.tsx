import React, { useState } from "react";
import {
  Card,
  Button,
  Intent,
  Callout,
  FormGroup,
  InputGroup,
} from "@blueprintjs/core";

import { registerStudent } from "../../services/api";
import FaceCapture from "../../components/FaceCapture";

interface Student {
  student_id: string;
  name: string;
  email: string;
}

const RegisterStudentPage: React.FC = () => {
  const [studentData, setStudentData] = useState<Student>({
    student_id: "",
    name: "",
    email: "",
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

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (images.length < 1) {
      setError("Please capture at least one image of the student.");
      return;
    }

    try {
      await registerStudent(studentData, images);
      setStudentData({ student_id: "", name: "", email: "" });
      setImages([]);
      alert("Student registered successfully!");
    } catch (error: any) {
      setError(
        error.response?.data?.error ||
          "Failed to register student. Please try again."
      );
    }
  };

  return (
    <Card>
      <h2>Register New Student</h2>
      {error && <Callout intent={Intent.DANGER}>{error}</Callout>}
      <form onSubmit={handleSubmit}>
        <FormGroup
          label="Student ID"
          labelFor="student_id-input"
          labelInfo="(required)"
        >
          <InputGroup
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
            id="email-input"
            name="email"
            placeholder="Enter email address"
            value={studentData.email}
            onChange={handleInputChange}
            type="email"
            required
          />
        </FormGroup>
        <FormGroup label="Student Image" labelFor="image-capture">
          <FaceCapture onCapture={setImages} />
        </FormGroup>
        <Button
          type="submit"
          intent={Intent.PRIMARY}
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

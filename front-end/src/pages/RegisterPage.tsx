// pages/RegisterPage.tsx
import React, { useState } from "react";
import {
  Card,
  FormGroup,
  InputGroup,
  Button,
  Intent,
  Callout,
} from "@blueprintjs/core";
import FaceCapture from "../components/FaceCapture";
import { registerStudent } from "../services/api";

const RegisterPage: React.FC = () => {
  const [name, setName] = useState("");
  const [studentId, setStudentId] = useState("");
  const [images, setImages] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // if (images.length < 5) {
    //   setError("Please capture at least 5 images.");
    //   return;
    // }

    if (
      name &&
      studentId
      // &&
      // images.length >= 5
    ) {
      try {
        await registerStudent(name, studentId, images);
        // Handle success (e.g., show toast, reset form)
        setName("");
        setStudentId("");
        setImages([]);
        alert("Student registered successfully!");
      } catch (error) {
        setError("Failed to register student. Please try again.");
      }
    }
  };

  return (
    <Card>
      <h2>Register New Student</h2>
      {error && <Callout intent={Intent.DANGER}>{error}</Callout>}
      <form onSubmit={handleSubmit}>
        <FormGroup label="Name" labelFor="name-input">
          <InputGroup
            id="name-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </FormGroup>
        <FormGroup label="Student ID" labelFor="id-input">
          <InputGroup
            id="id-input"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
          />
        </FormGroup>
        <FaceCapture onCapture={setImages} />
        <Button
          type="submit"
          intent={Intent.PRIMARY}
          text="Register"
          disabled={
            !name || !studentId
            // || images.length < 5
          }
        />
      </form>
    </Card>
  );
};

export default RegisterPage;

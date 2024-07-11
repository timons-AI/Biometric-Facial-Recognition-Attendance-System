import React, { useState } from "react";
import { Button, FormGroup, InputGroup, Intent, Card } from "@blueprintjs/core";
import { register } from "../api/api";
import { showToast } from "./Toaster";
import FaceCapture from "./FaceCapture";

const RegistrationForm: React.FC = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    role: "student",
    name: "",
    student_Id: "",
    year: "",
    academic_year: "",
    unit: "",
    group: "",
    semester: "",
  });

  const [faceImages, setFaceImages] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const userData = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        userData.append(key, value);
      });
      faceImages.forEach((image, index) => {
        userData.append(`faceImage${index}`, image);
      });

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
    <Card elevation={2} className="w-full max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">Register</h2>
      <form onSubmit={handleSubmit}>
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
        <FormGroup label="Role" labelFor="role-select">
          <select
            id="role-select"
            name="role"
            value={formData.role}
            onChange={handleInputChange}
            className="w-full p-2 border rounded"
          >
            <option value="student">Student</option>
            <option value="lecturer">Lecturer</option>
          </select>
        </FormGroup>
        <FormGroup label="Name" labelFor="name-input">
          <InputGroup
            id="name-input"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
          />
        </FormGroup>
        {formData.role === "student" && (
          <>
            <FormGroup label="Student ID" labelFor="studentId-input">
              <InputGroup
                id="studentId-input"
                name="studentId"
                value={formData.student_Id}
                onChange={handleInputChange}
                required
              />
            </FormGroup>
            <FormGroup label="Year" labelFor="year-input">
              <InputGroup
                id="year-input"
                name="year"
                type="number"
                value={formData.year}
                onChange={handleInputChange}
                required
              />
            </FormGroup>
            <FormGroup label="Academic Year" labelFor="academicYear-input">
              <InputGroup
                id="academicYear-input"
                name="academicYear"
                value={formData.academic_year}
                onChange={handleInputChange}
                required
              />
            </FormGroup>
            <FormGroup label="Unit" labelFor="unit-input">
              <InputGroup
                id="unit-input"
                name="unit"
                value={formData.unit}
                onChange={handleInputChange}
                required
              />
            </FormGroup>
            <FormGroup label="Group" labelFor="group-input">
              <InputGroup
                id="group-input"
                name="group"
                value={formData.group}
                onChange={handleInputChange}
                required
              />
            </FormGroup>
            <FormGroup label="Semester" labelFor="semester-input">
              <InputGroup
                id="semester-input"
                name="semester"
                value={formData.semester}
                onChange={handleInputChange}
                required
              />
            </FormGroup>
            <FormGroup label="Face Images" labelFor="faceImages-input">
              {/* <input
                id="faceImages-input"
                type="file"
                accept="image/*"
                multiple
                onChange={handleFileChange}
                required
              /> */}
              <FaceCapture onCapture={setFaceImages} />
            </FormGroup>
          </>
        )}
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

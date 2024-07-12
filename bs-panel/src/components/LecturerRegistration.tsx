import React, { useState } from "react";
import { Button, FormGroup, InputGroup, Intent, Card } from "@blueprintjs/core";
import { register } from "../api/api";
import { showToast } from "./Toaster";

const LecturerRegistration: React.FC = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    role: "lecturer",
    name: "",
    student_Id: "",
    year: "",
    academic_year: "",
    unit: "",
    group: "",
    semester: "",
  });

  const [faceImages] = useState<File[]>([]);
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
        <FormGroup label="Name" labelFor="name-input">
          <InputGroup
            id="name-input"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
          />
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

export default LecturerRegistration;

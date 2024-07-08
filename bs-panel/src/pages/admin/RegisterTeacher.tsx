import React, { useState } from "react";
import {
  Card,
  Button,
  Intent,
  Callout,
  FormGroup,
  InputGroup,
} from "@blueprintjs/core";
import { registerLecturer } from "../../services/api";

interface Lecturer {
  name: string;
  email: string;
  password: string;
}

const RegisterLecturerPage: React.FC = () => {
  const [lecturerData, setLecturerData] = useState<Lecturer>({
    name: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setLecturerData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    try {
      await registerLecturer(lecturerData);
      setLecturerData({ name: "", email: "", password: "" });
      alert("Lecturer registered successfully!");
    } catch (error: any) {
      setError(
        error.response?.data?.error ||
          "Failed to register lecturer. Please try again."
      );
    }
  };

  return (
    <Card>
      <h2>Register New Lecturer</h2>
      {error && <Callout intent={Intent.DANGER}>{error}</Callout>}
      <form onSubmit={handleSubmit}>
        <FormGroup label="Name" labelFor="name-input" labelInfo="(required)">
          <InputGroup
            id="name-input"
            name="name"
            placeholder="Enter full name"
            value={lecturerData.name}
            onChange={handleInputChange}
            required
          />
        </FormGroup>
        <FormGroup label="Email" labelFor="email-input" labelInfo="(required)">
          <InputGroup
            id="email-input"
            name="email"
            placeholder="Enter email address"
            value={lecturerData.email}
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
            id="password-input"
            name="password"
            placeholder="Enter password"
            value={lecturerData.password}
            onChange={handleInputChange}
            type="password"
            required
          />
        </FormGroup>
        <Button
          type="submit"
          intent={Intent.PRIMARY}
          text="Register Lecturer"
          disabled={
            !lecturerData.name || !lecturerData.email || !lecturerData.password
          }
        />
      </form>
    </Card>
  );
};

export default RegisterLecturerPage;

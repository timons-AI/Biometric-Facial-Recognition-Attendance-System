import React, { useState } from "react";
import {
  Button,
  FormGroup,
  InputGroup,
  Intent,
  Card,
  Callout,
} from "@blueprintjs/core";
import { registerAdmin } from "../api/api";
import { showToast } from "./Toaster";

const AdminRegistration: React.FC = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await registerAdmin(formData);
      showToast("Admin registered successfully", Intent.SUCCESS);
    } catch (error) {
      console.error("Admin registration failed:", error);
      showToast("Admin registration failed", Intent.DANGER);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card elevation={2} className="w-full max-w-md mx-auto">
      <Callout intent={Intent.WARNING} title="Temporary Feature">
        This admin registration page is temporary and should be removed or
        secured in production.
      </Callout>
      <h2 className="text-2xl font-bold mb-4 mt-4">Admin Registration</h2>
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
        <Button
          type="submit"
          intent={Intent.PRIMARY}
          text="Register Admin"
          className="w-full mt-4"
        />
      </form>
    </Card>
  );
};

export default AdminRegistration;

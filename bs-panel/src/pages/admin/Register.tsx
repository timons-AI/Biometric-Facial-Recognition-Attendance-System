// src/pages/admin/AdminRegistration.tsx

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  FormGroup,
  InputGroup,
  Button,
  Intent,
  Callout,
} from "@blueprintjs/core";
import { registerAdmin } from "../../services/api";

const AdminRegistration: React.FC = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!name || !email || !password) {
      setError("All fields are required");
      return;
    }

    try {
      await registerAdmin(name, email, password);
      setSuccess("Admin registered successfully");
      // Optionally, redirect to admin dashboard or login page
      setTimeout(() => navigate("/admin/dashboard"), 2000);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Registration failed");
    }
  };

  return (
    <Card elevation={2} className="admin-registration">
      <h2>Register New Admin</h2>
      {error && <Callout intent={Intent.DANGER}>{error}</Callout>}
      {success && <Callout intent={Intent.SUCCESS}>{success}</Callout>}
      <form onSubmit={handleSubmit}>
        <FormGroup label="Name" labelFor="name-input" labelInfo="(required)">
          <InputGroup
            id="name-input"
            placeholder="Enter full name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </FormGroup>
        <FormGroup label="Email" labelFor="email-input" labelInfo="(required)">
          <InputGroup
            id="email-input"
            type="email"
            placeholder="Enter email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </FormGroup>
        <Button type="submit" intent={Intent.PRIMARY} text="Register Admin" />
      </form>
    </Card>
  );
};

export default AdminRegistration;

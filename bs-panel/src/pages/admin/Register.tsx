import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  FormGroup,
  InputGroup,
  Button,
  Intent,
  H2,
} from "@blueprintjs/core";
import api from "../../services/api";

const AdminRegister: React.FC = () => {
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await api.post("/admin/register", {
        password,
        name,
        email,
      });
      alert("Administrator registered successfully!");
      navigate("/admin/login");
    } catch (error) {
      console.error("Registration failed:", error);
      alert("Failed to register administrator. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card elevation={2}>
      <H2>Register Administrator</H2>
      <form onSubmit={handleRegister}>
        <FormGroup label="Name" labelFor="name-input">
          <InputGroup
            id="name-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </FormGroup>
        <FormGroup label="Email" labelFor="email-input">
          <InputGroup
            id="email-input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </FormGroup>
        <FormGroup label="Password" labelFor="password-input">
          <InputGroup
            id="password-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </FormGroup>
        <Button type="submit" intent={Intent.PRIMARY} loading={isLoading}>
          Register
        </Button>
      </form>
    </Card>
  );
};

export default AdminRegister;

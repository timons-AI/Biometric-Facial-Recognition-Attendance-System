// src/pages/LoginPage.tsx

import React, { useState } from "react";
import { useSetAtom } from "jotai";
import { useNavigate } from "react-router-dom";
import {
  Card,
  FormGroup,
  InputGroup,
  Button,
  Intent,
  Callout,
} from "@blueprintjs/core";
import { userAtom } from "../store/auth";
import { login } from "../services/api";

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const setUser = useSetAtom(userAtom);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const userData = await login(email, password);
      setUser(userData);
      localStorage.setItem("token", userData.access_token);
      localStorage.setItem("user", JSON.stringify(userData));

      switch (userData.role) {
        case "student":
          navigate("/student/dashboard");
          break;
        case "lecturer":
          navigate("/lecturer/dashboard");
          break;
        case "admin":
          navigate("/admin/dashboard");
          break;
        default:
          navigate("/dashboard");
      }
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "An unexpected error occurred"
      );
    }
  };

  return (
    <Card>
      <h2>Login</h2>
      {error && <Callout intent={Intent.DANGER}>{error}</Callout>}
      <form onSubmit={handleSubmit}>
        <FormGroup label="Email" labelFor="email-input">
          <InputGroup
            id="email-input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </FormGroup>
        <FormGroup label="Password" labelFor="password-input">
          <InputGroup
            id="password-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </FormGroup>
        <Button type="submit" intent={Intent.PRIMARY}>
          Login
        </Button>
      </form>
    </Card>
  );
};

export default LoginPage;

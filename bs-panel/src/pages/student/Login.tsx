import React, { useState } from "react";
import { useSetAtom } from "jotai";
import { useNavigate } from "react-router-dom";
import {
  Button,
  Callout,
  Card,
  FormGroup,
  H2,
  InputGroup,
  Intent,
} from "@blueprintjs/core";
import { studentLogin } from "../../services/api";
import { userAtom } from "../../store/auth";

const StudentLoginPage: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const setUser = useSetAtom(userAtom);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const userData = await studentLogin(email, password);
      setUser({
        id: userData.student_id,
        role: "student",
        name: userData.name, // Assuming the API returns the student's name
        token: userData.access_token,
      });
      localStorage.setItem("token", userData.access_token);
      localStorage.setItem(
        "user",
        JSON.stringify({
          id: userData.student_id,
          role: "student",
          name: userData.name,
        })
      );
      console.log("Student login successful!");
      navigate("/student/dashboard");
    } catch (error) {
      console.error("Student login failed:", error);
      setError("Login failed. Please check your credentials and try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <H2>Student Login</H2>
      {error && <Callout intent={Intent.DANGER}>{error}</Callout>}
      <form onSubmit={handleLogin}>
        <FormGroup label="Email" labelFor="email-input">
          <InputGroup
            id="email-input"
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </FormGroup>
        <FormGroup label="Password" labelFor="password-input">
          <InputGroup
            id="password-input"
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </FormGroup>
        <Button
          type="submit"
          intent={Intent.PRIMARY}
          text="Login"
          loading={isLoading}
        />
      </form>
    </Card>
  );
};

export default StudentLoginPage;

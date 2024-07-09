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
import { loginLecturer } from "../../services/auth";
import { userAtom } from "../../store/auth";

const LecturerLogin: React.FC = () => {
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
      const userData = await loginLecturer(email, password);
      setUser({
        id: userData.id,
        role: userData.role,
        name: userData.name,
        token: userData.access_token,
      });
      localStorage.setItem("token", userData.access_token);
      localStorage.setItem(
        "user",
        JSON.stringify({
          id: userData.id,
          role: userData.role,
          name: userData.name,
        })
      );
      console.log("Login successful!");
      navigate("/lecturer/dashboard");
    } catch (error) {
      console.error("Login failed:", error);
      setError("Login failed. Please check your credentials and try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      {/* <img src="https://via.placeholder.com/150" alt="Lecturer" /> */}
      <H2>Lecturer Login</H2>
      {error && <Callout intent={Intent.DANGER}>{error}</Callout>}
      <form onSubmit={handleLogin}>
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
        <Button type="submit" fill intent={Intent.PRIMARY} loading={isLoading}>
          Log In
        </Button>
      </form>
    </Card>
  );
};

export default LecturerLogin;

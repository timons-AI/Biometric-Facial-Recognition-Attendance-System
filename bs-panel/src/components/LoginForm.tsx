import React, { useState } from "react";
import { useSetAtom } from "jotai";
import { useNavigate } from "react-router-dom";
import { Button, FormGroup, InputGroup, Intent, Card } from "@blueprintjs/core";
import { login } from "../api/api";
import { userAtom, isAuthenticatedAtom } from "../store/auth";
import { showToast } from "./Toaster";
import LoadingSpinner from "./LoadingSpinner";

const LoginForm: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const setUser = useSetAtom(userAtom);
  const setIsAuthenticated = useSetAtom(isAuthenticatedAtom);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const userData = await login(email, password);
      setUser(userData);
      setIsAuthenticated(true);
      showToast("Logged in successfully", Intent.SUCCESS);

      // Redirect based on user role
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
          navigate("/");
      }
    } catch (error: any) {
      console.error("Login failed:", error);
      console.log("Login failed:", error.response.data.msg);
      showToast(
        error ? error.response.data.msg : "Login failed. Please try again.",
        Intent.DANGER
      );
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <Card elevation={2} className="w-full max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">Login</h2>
      <form onSubmit={handleSubmit}>
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
        <Button
          type="submit"
          intent={Intent.PRIMARY}
          text="Login"
          className="w-full mt-4"
          loading={isLoading}
        />
      </form>
    </Card>
  );
};

export default LoginForm;

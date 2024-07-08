import React, { useState } from "react";
import { useSetAtom } from "jotai";
import { useNavigate } from "react-router-dom";
import {
  Button,
  Card,
  FormGroup,
  H2,
  InputGroup,
  Intent,
  Callout,
} from "@blueprintjs/core";
import { loginAdmin } from "../../services/auth";
import { userAtom } from "../../store/auth";
// import { toast } from 'react-toastify';

const AdminLogin: React.FC = () => {
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
      const userData = await loginAdmin(email, password);
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
      // toast.success("Login successful!");
      console.log("Login successful!");
      navigate("/admin/dashboard");
    } catch (error) {
      console.error("Login failed:", error);
      setError("Login failed. Please check your credentials and try again.");
      // toast.error("Login failed. Please try again.");
      console.log("Login failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card elevation={2}>
      <H2>Admin Login</H2>
      {error && <Callout intent={Intent.DANGER}>{error}</Callout>}
      <form onSubmit={handleLogin}>
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
          Log In
        </Button>
      </form>
    </Card>
  );
};

export default AdminLogin;

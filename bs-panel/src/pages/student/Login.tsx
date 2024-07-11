// src/pages/student/Login.tsx

import React, { useState } from "react";
import { useSetAtom } from "jotai";
import { useNavigate } from "react-router-dom";
import { Button, Card, H2, Callout, Intent } from "@blueprintjs/core";
import FaceCapture from "../../components/FaceCapture";
import { studentFaceLogin } from "../../services/api";
import { userAtom } from "../../store/auth";

const StudentLogin: React.FC = () => {
  const [capturedImages, setCapturedImages] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const setUser = useSetAtom(userAtom);
  const navigate = useNavigate();

  const handleLogin = async () => {
    if (capturedImages.length > 0) {
      try {
        // Convert the first captured image to a base64 string
        const reader = new FileReader();
        reader.readAsDataURL(capturedImages[0]);
        reader.onloadend = async () => {
          const base64Image = reader.result as string;
          const userData = await studentFaceLogin(base64Image);
          setUser({
            id: userData.student_id,
            role: "student",
            name: userData.name,
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
          navigate("/student/dashboard");
        };
      } catch (error) {
        setError("Login failed. Please try again.");
      }
    }
  };

  return (
    <Card>
      <H2>Student Login</H2>
      {error && <Callout intent={Intent.DANGER}>{error}</Callout>}
      <FaceCapture onCapture={setCapturedImages} />
      <Button
        intent="primary"
        onClick={handleLogin}
        disabled={capturedImages.length === 0}
      >
        Login
      </Button>
    </Card>
  );
};

export default StudentLogin;

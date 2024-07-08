import React, { useState } from "react";
import { useSetAtom } from "jotai";
import { useNavigate } from "react-router-dom";
import { Button, Card, H2, Intent, Spinner } from "@blueprintjs/core";
import { loginStudent } from "../../services/auth";
import { userAtom } from "../../store/auth";

const StudentLogin: React.FC = () => {
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const setUser = useSetAtom(userAtom);
  const navigate = useNavigate();

  const handleStartFaceRecognition = () => {
    setIsCameraActive(true);
    // Implement face recognition logic here
    // For demonstration, we'll use a timeout to simulate the process
    setTimeout(() => {
      const simulatedFaceId = "face_123";
      handleFaceRecognized(simulatedFaceId);
    }, 3000);
  };

  const handleFaceRecognized = async (faceId: string) => {
    setIsLoading(true);
    try {
      const userData = await loginStudent(faceId);
      setUser({
        id: userData.id,
        role: "student",
        name: userData.name,
        token: userData.token,
      });
      localStorage.setItem("token", userData.token);
      navigate("/student/dashboard");
    } catch (error) {
      console.error("Face recognition failed:", error);
    } finally {
      setIsLoading(false);
      setIsCameraActive(false);
    }
  };

  return (
    <Card elevation={2}>
      <H2>Student Login</H2>
      {!isCameraActive ? (
        <Button
          onClick={handleStartFaceRecognition}
          intent={Intent.PRIMARY}
          disabled={isLoading}
        >
          Start Face Recognition
        </Button>
      ) : (
        <div>
          {isLoading ? <Spinner /> : <p>Face recognition in progress...</p>}
        </div>
      )}
    </Card>
  );
};

export default StudentLogin;

import React, { useState } from "react";
import { Card, Button } from "@blueprintjs/core";
import FaceCapture from "../components/FaceCapture";
import { recognizeStudent } from "../services/api";

const RecognitionPage: React.FC = () => {
  const [recognizedStudent, setRecognizedStudent] = useState<string | null>(
    null
  );

  const handleRecognize = async (image: File) => {
    const student = await recognizeStudent(image);
    setRecognizedStudent(student);
  };

  return (
    <Card>
      <h2>Take Attendance</h2>
      <FaceCapture
        onCapture={(images) => handleRecognize(images[0])}
        singleCapture
      />
      {recognizedStudent ? (
        <p>
          Recognized student: <strong>{recognizedStudent}</strong>
        </p>
      ) : (
        <p>No student recognized</p>
      )}
    </Card>
  );
};

export default RecognitionPage;

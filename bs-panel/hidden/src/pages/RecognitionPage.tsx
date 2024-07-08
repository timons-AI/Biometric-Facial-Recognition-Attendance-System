import React, { useState } from "react";
import { Card, Button } from "@blueprintjs/core";
import FaceCapture from "../components/FaceCapture";
import { recognizeStudent } from "../services/api";
import TimetableComponent from "../components/Timetable";

interface Student {
  name: string;
  student_id: string;
}

const RecognitionPage: React.FC = () => {
  const [recognizedStudent, setRecognizedStudent] = useState<Student | null>(
    null
  );

  const handleRecognize = async (image: File) => {
    const student = await recognizeStudent(image);
    setRecognizedStudent(student);
  };

  return (
    <Card className="grid">
      <div className="flex flex-col">
        <h2>Take Attendance</h2>
        <FaceCapture
          onCapture={(images) => handleRecognize(images[0])}
          singleCapture
        />
        {recognizedStudent ? (
          <p>
            Recognized student: <strong>{recognizedStudent.name}</strong> (ID:{" "}
            {recognizedStudent.student_id})
          </p>
        ) : (
          <p>No student recognized</p>
        )}
      </div>
    </Card>
  );
};

export default RecognitionPage;

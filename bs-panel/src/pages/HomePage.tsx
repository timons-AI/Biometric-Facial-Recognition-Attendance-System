import React from "react";
import { H1 } from "@blueprintjs/core";
const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen  flex flex-col items-center justify-center">
      <main className="flex-grow container mx-auto px-4 py-16 text-center">
        <H1 className="text-4xl font-bold mb-4">
          Welcome to the Attendance System
        </H1>
        <p className="text-xl mb-8">
          {" "}
          This is the University Attendance System. It's a system that allows
          students to log in and view their attendance records. Lecturers can
          also log in to mark attendance for their classes. Admins can manage
          students, lecturers, and courses.
        </p>
      </main>
      <footer className="w-full bg-gray-800 text-white py-4">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 University Attendance System. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;

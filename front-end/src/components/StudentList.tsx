import React, { useEffect, useState } from "react";
import { HTMLTable } from "@blueprintjs/core";
import { getStudents } from "../services/api";
import { Student } from "../types";

const StudentList: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);

  useEffect(() => {
    const fetchStudents = async () => {
      const studentList = await getStudents();
      setStudents(studentList);
    };
    fetchStudents();
  }, []);

  return (
    <HTMLTable>
      <thead>
        <tr>
          <th>Name</th>
          <th>Student ID</th>
        </tr>
      </thead>
      <tbody>
        {students.map((student) => (
          <tr key={student.id}>
            <td>{student.name}</td>
            <td>{student.student_id}</td>
          </tr>
        ))}
      </tbody>
    </HTMLTable>
  );
};

export default StudentList;

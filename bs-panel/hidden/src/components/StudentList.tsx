import React, { useState, useEffect } from "react";
import { Spinner } from "@blueprintjs/core";
import { Cell, Column, Table2 } from "@blueprintjs/table";
import { getStudents } from "../services/api";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/table/lib/css/table.css";

interface Student {
  id: number;
  student_id: string;
  name: string;
  email: string;
  academic_year: number;
  semester: string;
  academic_type: string;
  academic_group: string;
}

const StudentList: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStudents = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const studentList = await getStudents();
        setStudents(studentList);
      } catch (err) {
        setError("An error occurred while fetching students");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStudents();
  }, []);

  if (isLoading) return <Spinner />;
  if (error) return <div className="bp4-text-danger">{error}</div>;

  const cellRenderer = (rowIndex: number, columnIndex: number) => {
    const student = students[rowIndex];
    switch (columnIndex) {
      case 0:
        return <Cell>{student.name}</Cell>;
      case 1:
        return <Cell>{student.student_id}</Cell>;
      case 2:
        return <Cell>{student.email}</Cell>;
      case 3:
        return <Cell>{student.academic_year}</Cell>;
      case 4:
        return <Cell>{student.semester}</Cell>;
      case 5:
        return <Cell>{student.academic_type}</Cell>;
      case 6:
        return <Cell>{student.academic_group}</Cell>;
      default:
        return <Cell />;
    }
  };

  return (
    <div className="flex flex-col">
      <h2 className="text-2xl font-semibold mb-4">Student List</h2>
      <div className="overflow-x-auto">
        <Table2
          numRows={students.length}
          columnWidths={[150, 100, 200, 100, 100, 150, 150]}
          className="min-w-full"
        >
          <Column
            name="Name"
            cellRenderer={(rowIndex) => cellRenderer(rowIndex, 0)}
          />
          <Column
            name="Student ID"
            cellRenderer={(rowIndex) => cellRenderer(rowIndex, 1)}
          />
          <Column
            name="Email"
            cellRenderer={(rowIndex) => cellRenderer(rowIndex, 2)}
          />
          <Column
            name="Academic Year"
            cellRenderer={(rowIndex) => cellRenderer(rowIndex, 3)}
          />
          <Column
            name="Semester"
            cellRenderer={(rowIndex) => cellRenderer(rowIndex, 4)}
          />
          <Column
            name="Academic Type"
            cellRenderer={(rowIndex) => cellRenderer(rowIndex, 5)}
          />
          <Column
            name="Academic Group"
            cellRenderer={(rowIndex) => cellRenderer(rowIndex, 6)}
          />
        </Table2>
      </div>
    </div>
  );
};

export default StudentList;

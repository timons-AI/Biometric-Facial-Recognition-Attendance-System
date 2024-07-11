// src/pages/admin/ApprovalPage.tsx

import React, { useEffect, useState } from "react";
import { Card, H2, Button, HTMLTable } from "@blueprintjs/core";
import {
  getStudentsForApproval,
  approveStudent,
  rejectStudent,
} from "../../services/api";

interface PendingStudent {
  student_id: string;
  name: string;
  email: string;
}

const AdminApprovalPage: React.FC = () => {
  const [pendingStudents, setPendingStudents] = useState<PendingStudent[]>([]);

  useEffect(() => {
    fetchPendingStudents();
  }, []);

  const fetchPendingStudents = async () => {
    const students = await getStudentsForApproval();
    setPendingStudents(students);
  };

  const handleApprove = async (studentId: string) => {
    await approveStudent(studentId);
    fetchPendingStudents();
  };

  const handleReject = async (studentId: string) => {
    await rejectStudent(studentId);
    fetchPendingStudents();
  };

  return (
    <Card>
      <H2>Student Approval</H2>
      <HTMLTable>
        <thead>
          <tr>
            <th>Student ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {pendingStudents.map((student) => (
            <tr key={student.student_id}>
              <td>{student.student_id}</td>
              <td>{student.name}</td>
              <td>{student.email}</td>
              <td>
                <Button
                  intent="success"
                  onClick={() => handleApprove(student.student_id)}
                >
                  Approve
                </Button>
                <Button
                  intent="danger"
                  onClick={() => handleReject(student.student_id)}
                >
                  Reject
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </HTMLTable>
    </Card>
  );
};

export default AdminApprovalPage;

import React, { useState, useEffect } from "react";
import { Button, Card, Elevation, HTMLTable, Intent } from "@blueprintjs/core";
import { getPendingRegistrations, approveUser, rejectUser } from "../api/api";
import { showToast } from "./Toaster";

interface PendingUser {
  id: number;
  email: string;
  role: string;
  name?: string;
  studentId?: string;
}

const AdminApproval: React.FC = () => {
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([]);

  useEffect(() => {
    fetchPendingRegistrations();
  }, []);

  const fetchPendingRegistrations = async () => {
    try {
      const data = await getPendingRegistrations();
      setPendingUsers(data);
    } catch (error) {
      console.error("Failed to fetch pending registrations:", error);
    }
  };

  const handleApprove = async (userId: number) => {
    try {
      await approveUser(userId);
      fetchPendingRegistrations();
      showToast("User approved", Intent.SUCCESS);
    } catch (error) {
      console.error("Failed to approve user:", error);
    }
  };

  const handleReject = async (userId: number) => {
    try {
      await rejectUser(userId);
      fetchPendingRegistrations();
      showToast("User rejected", Intent.DANGER);
    } catch (error) {
      console.error("Failed to reject user:", error);
    }
  };

  return (
    <Card elevation={Elevation.TWO} className="w-full max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Pending Registrations</h2>
      <HTMLTable className="w-full">
        <thead>
          <tr>
            <th>Email</th>
            <th>Role</th>
            <th>Name</th>
            <th>Student ID</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {pendingUsers.map((user) => (
            <tr key={user.id}>
              <td>{user.email}</td>
              <td>{user.role}</td>
              <td>{user.name || "-"}</td>
              <td>{user.studentId || "-"}</td>
              <td>
                <Button
                  intent={Intent.SUCCESS}
                  icon="tick"
                  onClick={() => handleApprove(user.id)}
                  className="mr-2"
                >
                  Approve
                </Button>
                <Button
                  intent={Intent.DANGER}
                  icon="cross"
                  onClick={() => handleReject(user.id)}
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

export default AdminApproval;

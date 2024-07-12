import React, { useState, useEffect } from "react";
import {
  Button,
  Card,
  Elevation,
  HTMLTable,
  Intent,
  Spinner,
  Tag,
} from "@blueprintjs/core";
import { getPendingRegistrations, approveUser, rejectUser } from "../api/api";
import { showToast } from "./Toaster";

interface PendingUser {
  user_id: number;
  email: string;
  role: string;
  name?: string;
  student_id?: string;
  academic_year_id?: number;
  course_id?: number;
  college_id?: number;
  semester_id?: number;
}

export interface PaginatedResponse {
  pending_registrations: PendingUser[];
  total_count: number;
  pages: number;
  current_page: number;
  per_page: number;
}

const AdminApproval: React.FC = () => {
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchPendingRegistrations(currentPage);
  }, [currentPage]);

  const fetchPendingRegistrations = async (page: number) => {
    setIsLoading(true);
    try {
      const data = await getPendingRegistrations(page);
      setPendingUsers(data.pending_registrations);
      setTotalPages(data.pages);
      setCurrentPage(data.current_page);
    } catch (error) {
      console.error("Failed to fetch pending registrations:", error);
      showToast("Failed to fetch pending registrations", Intent.DANGER);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async (userId: number) => {
    try {
      await approveUser(userId);
      fetchPendingRegistrations(currentPage);
      showToast("User approved", Intent.SUCCESS);
    } catch (error) {
      console.error("Failed to approve user:", error);
      showToast("Failed to approve user", Intent.DANGER);
    }
  };

  const handleReject = async (userId: number) => {
    try {
      await rejectUser(userId);
      fetchPendingRegistrations(currentPage);
      showToast("User rejected", Intent.DANGER);
    } catch (error) {
      console.error("Failed to reject user:", error);
      showToast("Failed to reject user", Intent.DANGER);
    }
  };

  const getRoleTag = (role: string) => {
    switch (role) {
      case "student":
        return <Tag intent={Intent.PRIMARY}>Student</Tag>;
      case "lecturer":
        return <Tag intent={Intent.SUCCESS}>Lecturer</Tag>;
      case "admin":
        return <Tag intent={Intent.WARNING}>Admin</Tag>;
      default:
        return <Tag>Unknown</Tag>;
    }
  };

  return (
    <Card elevation={Elevation.TWO} className="w-full max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Pending Registrations</h2>
      {isLoading ? (
        <Spinner />
      ) : (
        <>
          <HTMLTable className="w-full">
            <thead>
              <tr>
                <th>Email</th>
                <th>Role</th>
                <th>Name</th>
                <th>ID</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {pendingUsers.map((user) => (
                <tr key={user.user_id}>
                  <td>{user.email}</td>
                  <td>{getRoleTag(user.role)}</td>
                  <td>{user.name || "-"}</td>
                  <td>{user.student_id || user.user_id}</td>
                  <td>
                    <Button
                      intent={Intent.SUCCESS}
                      icon="tick"
                      onClick={() => handleApprove(user.user_id)}
                      className="mr-2"
                    >
                      Approve
                    </Button>
                    <Button
                      intent={Intent.DANGER}
                      icon="cross"
                      onClick={() => handleReject(user.user_id)}
                    >
                      Reject
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </HTMLTable>
          <div className="mt-4 flex justify-between items-center">
            <Button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
            >
              Previous
            </Button>
            <span>
              Page {currentPage} of {totalPages}
            </span>
            <Button
              disabled={currentPage === totalPages}
              onClick={() =>
                setCurrentPage((prev) => Math.min(prev + 1, totalPages))
              }
            >
              Next
            </Button>
          </div>
        </>
      )}
    </Card>
  );
};

export default AdminApproval;

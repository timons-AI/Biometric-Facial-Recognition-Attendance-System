import React from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import { useAtom } from "jotai";
import { isAuthenticatedAtom, userAtom } from "./store/auth";
import AppNavbar from "./components/Navbar";
import RegistrationForm from "./components/RegsitrationForm";
import LoginForm from "./components/LoginForm";
import AdminApproval from "./components/AdminApproval";
import StudentDashboard from "./components/StudentDashboard";
import LecturerDashboard from "./components/LecturerDashboard";
import AdminDashboard from "./components/AdminDashboard";
import AdminRegistration from "./components/AdminRegistrationForm";
import StudentViewPortal from "./components/StudentViewPortal";
import PageNotFound from "./components/PageNotFound";
import AdminTimetableManagement from "./components/AdminTimeTableMgt";
import LecturerRegistration from "./components/LecturerRegistration";
import AdminReportsDashboard from "./components/AdminReport";

const App: React.FC = () => {
  const [isAuthenticated] = useAtom(isAuthenticatedAtom);
  const [user] = useAtom(userAtom);

  const PrivateRoute: React.FC<{
    element: React.ReactElement;
    allowedRoles: string[];
  }> = ({ element, allowedRoles }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" />;
    }
    if (user && !allowedRoles.includes(user.role)) {
      return <Navigate to="/" />;
    }
    return element;
  };

  return (
    <Router>
      <AppNavbar />
      <div className="container mx-auto mt-4">
        <Routes>
          <Route path="/register" element={<RegistrationForm />} />
          <Route path="/login" element={<LoginForm />} />
          <Route path="/student-portal" element={<StudentViewPortal />} />
          <Route path="/admin/reports" element={<AdminReportsDashboard />} />
          <Route
            path="/student/dashboard"
            element={
              <PrivateRoute
                element={<StudentDashboard />}
                allowedRoles={["student"]}
              />
            }
          />
          <Route
            path="/lecturer/dashboard"
            element={
              <PrivateRoute
                element={<LecturerDashboard />}
                allowedRoles={["lecturer"]}
              />
            }
          />
          <Route
            path="/admin/dashboard"
            element={
              <PrivateRoute
                element={<AdminDashboard />}
                allowedRoles={["admin"]}
              />
            }
          />
          <Route
            path="/admin/approve-students"
            element={
              <PrivateRoute
                element={<AdminApproval />}
                allowedRoles={["admin"]}
              />
            }
          />

          <Route path="/admin/register-admin" element={<AdminRegistration />} />
          <Route
            path="/admin/register-lecturer"
            element={<LecturerRegistration />}
          />
          <Route
            path="/admin/timetable-management"
            element={
              <PrivateRoute
                element={<AdminTimetableManagement />}
                allowedRoles={["admin"]}
              />
            }
          />

          <Route path="/" element={<Navigate to="/login" replace />} />
          {/* pages that don't exist */}
          <Route path="*" element={<PageNotFound />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;

import React, { useEffect, useRef } from "react";
import {
  // BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useNavigate,
} from "react-router-dom";
import { useAtom } from "jotai";
import { userAtom } from "./store/auth";
import AppNavbar from "./components/Navbar";
import StudentLogin from "./pages/student/Login";
import LecturerLogin from "./pages/lecturer/Login";
import AdminLogin from "./pages/admin/Login";
import HomePage from "./pages/HomePage";
import AdminRegister from "./pages/admin/Register";
import StudentDashboard from "./pages/student/Dashboard";
import LecturerDashboard from "./pages/lecturer/Dashboard";
import AdminDashboard from "./pages/admin/Dashboard";
import RegisterStudentPage from "./pages/admin/RegisterStudent";
import RegisterLecturerPage from "./pages/admin/RegisterTeacher";
import { checkSessionExpiration, useLogout } from "./utils/sessionManager";

const App: React.FC = () => {
  const [user, setUser] = useAtom(userAtom);
  const navigate = useNavigate();
  const logout = useLogout();
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const userData = localStorage.getItem("user");

    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser({
          id: parsedUser.id,
          role: parsedUser.role,
          name: parsedUser.name,
          token: token,
        });

        // Check session expiration
        if (checkSessionExpiration()) {
          logout();
          navigate("/");
        }
      } catch (error) {
        console.error("Error parsing user data:", error);
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    }

    // Set up interval to check session expiration
    intervalRef.current = window.setInterval(() => {
      if (checkSessionExpiration()) {
        logout();
        navigate("/");
      }
    }, 60000); // Check every minute

    return () => {
      if (intervalRef.current !== null) {
        clearInterval(intervalRef.current);
      }
    };
  }, [setUser, logout, navigate]);

  const PrivateRoute: React.FC<{
    element: React.ReactElement;
    allowedRoles: string[];
  }> = ({ element, allowedRoles }) => {
    if (!user) {
      return <Navigate to="/" />;
    }
    if (!allowedRoles.includes(user.role)) {
      return <Navigate to="/" />;
    }
    return element;
  };

  return (
    // <Router>
    <>
      <AppNavbar />
      <div className="container p-2 mt-4">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/student/login" element={<StudentLogin />} />
          <Route path="/lecturer/login" element={<LecturerLogin />} />
          <Route path="/admin/login" element={<AdminLogin />} />
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
            path="/admin/register"
            element={
              <PrivateRoute
                element={<AdminRegister />}
                allowedRoles={["admin"]}
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
            path="/admin/register-student"
            element={
              <PrivateRoute
                element={<RegisterStudentPage />}
                allowedRoles={["admin"]}
              />
            }
          />
          <Route
            path="/admin/register-lecturer"
            element={
              <PrivateRoute
                element={<RegisterLecturerPage />}
                allowedRoles={["admin"]}
              />
            }
          />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </>
    // </Router>
  );
};

export default App;

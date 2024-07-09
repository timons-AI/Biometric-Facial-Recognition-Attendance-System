import React, { useEffect, useRef, lazy, Suspense } from "react";
import {
  Routes,
  Route,
  Navigate,
  useNavigate,
  BrowserRouter as Router,
} from "react-router-dom";
import { useAtom } from "jotai";
import { userAtom } from "./store/auth";
import AppNavbar from "./components/Navbar";
import { Spinner } from "@blueprintjs/core";
import { useSessionCheck } from "./hooks/useSessionCheck";
import StartSessionPage from "./pages/student/StartSession";

const HomePage = lazy(() => import("./pages/HomePage"));
const StudentLogin = lazy(() => import("./pages/student/Login"));
const LecturerLogin = lazy(() => import("./pages/lecturer/Login"));
const AdminLogin = lazy(() => import("./pages/admin/Login"));
const AdminRegister = lazy(() => import("./pages/admin/Register"));
const StudentDashboard = lazy(() => import("./pages/student/Dashboard"));
const LecturerDashboard = lazy(() => import("./pages/lecturer/Dashboard"));
const AdminDashboard = lazy(() => import("./pages/admin/Dashboard"));
const RegisterStudentPage = lazy(() => import("./pages/admin/RegisterStudent"));
const RegisterLecturerPage = lazy(
  () => import("./pages/admin/RegisterTeacher")
);

const App: React.FC = () => {
  const [user, setUser] = useAtom(userAtom);
  useSessionCheck();

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
      <div className="flex flex-col items-center justify-center min-h-screen">
        <Suspense fallback={<Spinner />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/student/login" element={<StudentLogin />} />
            <Route path="/lecturer/login" element={<LecturerLogin />} />
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route
              path="/student/start-session"
              element={
                <PrivateRoute
                  element={<StartSessionPage />}
                  allowedRoles={["student"]}
                />
              }
            />
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
        </Suspense>
      </div>
    </>
    // </Router>
  );
};

export default App;

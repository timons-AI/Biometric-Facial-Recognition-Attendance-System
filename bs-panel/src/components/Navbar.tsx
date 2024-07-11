import React from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Button,
  Navbar,
  Alignment,
  Menu,
  MenuItem,
  Popover,
  Position,
} from "@blueprintjs/core";
import { useAtom } from "jotai";
import { userAtom, isAuthenticatedAtom } from "../store/auth";
import { showToast } from "./Toaster";

const AppNavbar: React.FC = () => {
  const [user, setUser] = useAtom(userAtom);
  const [, setIsAuthenticated] = useAtom(isAuthenticatedAtom);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
    setIsAuthenticated(false);
    showToast("Logged out successfully", "success");
    navigate("/login");
  };

  const renderMenu = () => {
    if (!user) return undefined;
    // console.log(user);

    let menuItems;
    switch (user.role) {
      case "student":
        menuItems = (
          <Menu>
            <MenuItem
              icon="dashboard"
              text="Dashboard"
              onClick={() => navigate("/student/dashboard")}
            />
            <MenuItem
              icon="calendar"
              text="Schedule"
              onClick={() => navigate("/student/schedule")}
            />
            <MenuItem
              icon="chart"
              text="Attendance Report"
              onClick={() => navigate("/student/attendance")}
            />
          </Menu>
        );
        break;
      case "lecturer":
        menuItems = (
          <Menu>
            <MenuItem
              icon="dashboard"
              text="Dashboard"
              onClick={() => navigate("/lecturer/dashboard")}
            />
            <MenuItem
              icon="people"
              text="My Courses"
              onClick={() => navigate("/lecturer/courses")}
            />
            <MenuItem
              icon="take-action"
              text="Mark Attendance"
              onClick={() => navigate("/lecturer/mark-attendance")}
            />
          </Menu>
        );
        break;
      case "admin":
        menuItems = (
          <Menu>
            <MenuItem
              icon="dashboard"
              text="Dashboard"
              onClick={() => navigate("/admin/dashboard")}
            />
            <MenuItem
              icon="new-person"
              text="Register User"
              onClick={() => navigate("/admin/register")}
            />
            <MenuItem
              icon="confirm"
              text="Approve Students"
              onClick={() => navigate("/admin/approve-students")}
            />
            <MenuItem
              icon="new-person"
              text="Register Admin"
              onClick={() => navigate("/admin/register-admin")}
            />
            <MenuItem
              icon="time"
              text="Timetable Management"
              onClick={() => navigate("/admin/timetable-management")}
            />
          </Menu>
        );
        break;
      default:
        menuItems = undefined;
    }

    return menuItems ? (
      <Popover content={menuItems} position={Position.BOTTOM_RIGHT}>
        <Button
          icon="user"
          rightIcon="caret-down"
          text={`${user.name} (${user.role})`}
          className="ml-2"
        />
      </Popover>
    ) : null;
  };

  return (
    <Navbar className="bp3-dark">
      <Navbar.Group align={Alignment.LEFT} className="flex items-center">
        <Navbar.Heading className="text-lg font-bold">
          Attendance System
        </Navbar.Heading>
        <Navbar.Divider />
        <Button
          icon="home"
          text="Home"
          minimal
          onClick={() => navigate("/")}
          className="bp3-minimal"
        />
        <Button
          icon="camera"
          text="Student Portal"
          minimal
          onClick={() => navigate("/student-portal")}
          className="bp3-minimal"
        />
      </Navbar.Group>
      <Navbar.Group align={Alignment.RIGHT} className="flex items-center">
        {user ? (
          <>
            {renderMenu()}
            <Button
              icon="log-out"
              text="Logout"
              minimal
              onClick={handleLogout}
              className="bp3-minimal"
            />
          </>
        ) : (
          <>
            <Button
              icon="log-in"
              text="Login"
              minimal
              onClick={() => navigate("/login")}
              className="bp3-minimal"
            />
            <Button
              icon="new-person"
              text="Register"
              minimal
              onClick={() => navigate("/register")}
              className="bp3-minimal"
            />
          </>
        )}
      </Navbar.Group>
    </Navbar>
  );
};

export default AppNavbar;

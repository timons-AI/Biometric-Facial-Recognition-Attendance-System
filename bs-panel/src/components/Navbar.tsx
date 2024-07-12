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
  Tag,
} from "@blueprintjs/core";
import { useAtom } from "jotai";
import { userAtom, isAuthenticatedAtom, darkModeAtom } from "../store/auth";
import { showToast } from "./Toaster";

const AppNavbar: React.FC = () => {
  const [user, setUser] = useAtom(userAtom);
  const [, setIsAuthenticated] = useAtom(isAuthenticatedAtom);
  const [isDarkMode, setIsDarkMode] = useAtom(darkModeAtom);

  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
    setIsAuthenticated(false);
    showToast("Logged out successfully", "success");
    navigate("/login");
  };

  const registrationMenu = (
    <Menu>
      <MenuItem
        icon="new-person"
        text="Register Student"
        // onClick={() => navigate("/admin/register-student")}
        onClick={() => navigate("/register")}
      />
      <MenuItem
        icon="new-person"
        text="Register Lecturer"
        onClick={() => navigate("/admin/register-lecturer")}
      />
      <MenuItem
        icon="new-person"
        text={
          <span>
            Register Admin{" "}
            <Tag minimal intent="warning">
              Temporary
            </Tag>
          </span>
        }
        onClick={() => navigate("/admin/register-admin")}
      />
    </Menu>
  );

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
            {/* <MenuItem
              icon="calendar"
              text="Schedule"
              onClick={() => navigate("/student/schedule")}
            />
            <MenuItem
              icon="chart"
              text="Attendance Report"
              onClick={() => navigate("/student/attendance")}
            /> */}
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
              text="Register Student"
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
              icon="people"
              text="Register Lecturer"
              onClick={() => navigate("/admin/register-lecturer")}
            />
            <MenuItem
              icon="time"
              // Tag with intent warning to indicate temporary feature
              // text="Timetable Management"
              text={
                <span className="flex flex-col">
                  Timetable Management{" "}
                  <Tag minimal intent="danger">
                    Under Construction
                  </Tag>
                </span>
              }
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
          text={
            <span>
              {user.name} <Tag intent="primary">{user.role}</Tag>
            </span>
          }
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
        {/* <Button
          icon="home"
          text="Home"
          minimal
          onClick={() => navigate("/")}
          className="bp3-minimal"
        /> */}
        <Button
          icon="camera"
          text="Student Portal"
          minimal
          onClick={() => navigate("/student-portal")}
          className="bp3-minimal"
        />
      </Navbar.Group>
      <Navbar.Group align={Alignment.RIGHT} className="flex items-center gap-1">
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
            {/* <Button
              icon="new-person"
              text="Register"
              minimal
              onClick={() => navigate("/register")}
              className="bp3-minimal"
            /> */}

            <Popover
              content={registrationMenu}
              position={Position.BOTTOM_RIGHT}
            >
              <Button
                icon="new-person"
                text="Register"
                // minimal
                rightIcon="caret-down"
                className="bp3-minimal"
              />
            </Popover>
          </>
        )}
        <Button
          icon={isDarkMode ? "flash" : "moon"}
          intent="none"
          onClick={() => setIsDarkMode((prev) => !prev)}
        />
      </Navbar.Group>
    </Navbar>
  );
};

export default AppNavbar;

import React from "react";
import { useAtom } from "jotai";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Navbar,
  Button,
  Alignment,
  Tag,
  Menu,
  MenuItem,
  Popover,
  Position,
} from "@blueprintjs/core";
import { userAtom } from "../store/auth";
import { logout } from "../services/auth";

const AppNavbar: React.FC = () => {
  const [user, setUser] = useAtom(userAtom);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    setUser(null);
    navigate("/");
  };

  const isActive = (path: string) => location.pathname === path;
  console.log(location.pathname);

  const renderLoginMenu = () => (
    <Popover
      content={
        <Menu>
          <MenuItem
            icon="user"
            text="Student Login"
            onClick={() => navigate("/student/login")}
          />
          <MenuItem
            icon="user"
            text="Lecturer Login"
            onClick={() => navigate("/lecturer/login")}
          />
          <MenuItem
            icon="key"
            text="Admin Login"
            onClick={() => navigate("/admin/login")}
          />
        </Menu>
      }
      position={Position.BOTTOM_RIGHT}
    >
      <Button icon="log-in" text="Login" rightIcon="caret-down" />
    </Popover>
  );

  const renderUserMenu = () => (
    <Popover
      content={
        <Menu>
          <MenuItem
            icon="dashboard"
            text="Dashboard"
            onClick={() => navigate(`/${user?.role}/dashboard`)}
          />
          {user?.role === "admin" && (
            <>
              <MenuItem
                icon="new-person"
                text="Register Admin"
                onClick={() => navigate("/admin/register")}
              />
              <MenuItem
                icon="new-object"
                text="Add Course"
                onClick={() => navigate("/admin/add-course")}
              />
            </>
          )}
          {user?.role === "lecturer" && (
            <MenuItem
              icon="timeline-events"
              text="Manage Sessions"
              onClick={() => navigate("/lecturer/manage-sessions")}
            />
          )}
          {user?.role === "student" && (
            <MenuItem
              icon="history"
              text="Attendance History"
              onClick={() => navigate("/student/attendance-history")}
            />
          )}
          <MenuItem icon="log-out" text="Logout" onClick={handleLogout} />
        </Menu>
      }
      position={Position.BOTTOM_RIGHT}
    >
      <Button
        icon="user"
        minimal
        intent="none"
        text={user?.name}
        rightIcon="caret-down"
      />
    </Popover>
  );

  const renderActionsMenu = () => (
    <Popover
      content={
        <Menu>
          <MenuItem
            icon="new-person"
            text="Register Student"
            onClick={() => navigate("/admin/register-student")}
          />
          <MenuItem
            icon="new-person"
            text="Register Lecturer"
            onClick={() => navigate("/admin/register-lecturer")}
          />
        </Menu>
      }
      position={Position.BOTTOM_RIGHT}
    >
      <Button icon="more" minimal intent="warning" rightIcon="caret-down" />
    </Popover>
  );

  return (
    <Navbar>
      <Navbar.Group align={Alignment.LEFT}>
        <Navbar.Heading>Attendance System</Navbar.Heading>
        <Navbar.Divider />
        <Button
          // className={isActive("/") ? " bg-red-400" : ""}
          icon="home"
          text="Home"
          intent={isActive("/") ? "primary" : "none"}
          minimal
          onClick={() => navigate("/")}
        />
        {user && (
          <Button
            // className={isActive(`/${user.role}/dashboard`) ? "bp4-active" : ""}
            intent={isActive(`/${user.role}/dashboard`) ? "primary" : "none"}
            icon="dashboard"
            text="Dashboard"
            minimal
            onClick={() => navigate(`/${user.role}/dashboard`)}
          />
        )}
      </Navbar.Group>
      <Navbar.Group align={Alignment.RIGHT}>
        {user ? renderUserMenu() : renderLoginMenu()}
      </Navbar.Group>
      <Navbar.Group align={Alignment.RIGHT}>
        {user && user.role === "admin" && renderActionsMenu()}
      </Navbar.Group>
    </Navbar>
  );
};

export default AppNavbar;

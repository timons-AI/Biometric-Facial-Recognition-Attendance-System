import React from "react";
import { Link } from "react-router-dom";
import { Navbar, Button, Alignment } from "@blueprintjs/core";

const Navigation: React.FC = () => {
  return (
    <Navbar>
      <Navbar.Group align={Alignment.LEFT}>
        <Navbar.Heading>Facial Recognition Attendance</Navbar.Heading>
        <Navbar.Divider />
        <Link to="/">
          <Button className="bp3-minimal" icon="home" text="Dashboard" />
        </Link>
        <Link to="/register">
          <Button className="bp3-minimal" icon="new-person" text="Register" />
        </Link>
        <Link to="/recognize">
          <Button
            className="bp3-minimal"
            icon="camera"
            text="Take Attendance"
          />
        </Link>
        <Link to="/attendance">
          <Button
            className="bp3-minimal"
            icon="timeline-events"
            text="Attendance List"
          />
        </Link>
      </Navbar.Group>
    </Navbar>
  );
};

export default Navigation;

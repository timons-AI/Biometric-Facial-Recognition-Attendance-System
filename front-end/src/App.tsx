// App.tsx
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { FocusStyleManager } from "@blueprintjs/core";
import Navigation from "./components/Navigation";
import DashboardPage from "./pages/DashboardPage";
import RegisterPage from "./pages/RegisterPage";
import RecognitionPage from "./pages/RecognitionPage";
import AttendancePage from "./pages/AttendancePage";
import AttendanceCapture from "./pages/Test";

FocusStyleManager.onlyShowFocusOnTabs();

const App: React.FC = () => {
  return (
    <Router>
      <Navigation />
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/testing" element={<AttendanceCapture />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/recognize" element={<RecognitionPage />} />
        <Route path="/attendance" element={<AttendancePage />} />
      </Routes>
    </Router>
  );
};

export default App;

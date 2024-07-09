import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAtom } from "jotai";

import { userAtom } from "../store/auth";
import { checkSessionExpiration, useLogout } from "../utils/sessionManager";

export function useSessionCheck() {
  const [user, setUser] = useAtom(userAtom);
  const navigate = useNavigate();
  const logout = useLogout();
  const [sessionExpired, setSessionExpired] = useState(false);

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
      } catch (error) {
        console.error("Error parsing user data:", error);
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    }

    const checkSession = () => {
      if (checkSessionExpiration()) {
        setSessionExpired(true);
      }
    };

    checkSession(); // Check immediately
    const checkInterval = window.setInterval(checkSession, 60000); // Check every minute

    return () => {
      clearInterval(checkInterval);
    };
  }, [setUser]);

  useEffect(() => {
    if (sessionExpired) {
      logout();
      navigate("/");
    }
  }, [sessionExpired, logout, navigate]);

  return sessionExpired;
}

import { jwtDecode } from "jwt-decode";
import { userAtom } from "../store/auth";
import { useSetAtom } from "jotai";

interface DecodedToken {
  exp: number;
}

export const checkSessionExpiration = () => {
  const token = localStorage.getItem("token");
  if (token) {
    const decodedToken = jwtDecode(token) as DecodedToken;
    const currentTime = Date.now() / 1000;

    if (decodedToken.exp < currentTime) {
      // Token has expired
      return true;
    }
  }
  return false;
};

export const useLogout = () => {
  const setUser = useSetAtom(userAtom);

  return () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };
};

import { atom } from "jotai";
import { jwtDecode } from "jwt-decode";

export interface User {
  id: string;
  name: string;
  email: string;
  role: "student" | "lecturer" | "admin";
}

const token = localStorage.getItem("token");
const initialUser = token ? (jwtDecode(token) as User) : null;

export const userAtom = atom<User | null>(initialUser);
export const isAuthenticatedAtom = atom<boolean>(!!initialUser);

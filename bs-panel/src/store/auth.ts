import { atom } from "jotai";

interface User {
  id: string;
  role: "student" | "lecturer" | "admin";
  name: string;
  token: string;
}

export const userAtom = atom<User | null>(null);

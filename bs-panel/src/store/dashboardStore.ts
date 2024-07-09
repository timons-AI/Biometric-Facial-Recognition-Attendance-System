import { atom } from "jotai";
import { AdminDashboardData } from "../pages/admin/Dashboard";
import { TeacherDashboardData } from "../pages/lecturer/Dashboard";

export const adminDashboardAtom = atom<AdminDashboardData | null>(null);
export const teacherDashboardAtom = atom<TeacherDashboardData | null>(null);
export const dashboardLoadingAtom = atom<boolean>(false);
export const dashboardErrorAtom = atom<string | null>(null);

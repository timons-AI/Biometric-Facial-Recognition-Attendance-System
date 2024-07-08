import axios from "axios";
import { AdminDashboardData } from "../pages/admin/Dashboard";

const API_URL = "http://localhost:5000/api";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
export default api;
interface Student {
  student_id: string;
  name: string;
  email: string;
}

interface Lecturer {
  name: string;
  email: string;
  password: string;
}
export const registerStudent = async (studentData: Student, images: File[]) => {
  const formData = new FormData();
  formData.append("student_id", studentData.student_id);
  formData.append("name", studentData.name);
  formData.append("email", studentData.email);
  images.forEach((image, index) => {
    formData.append("files", image, `face_${index}.jpg`);
  });

  const response = await api.post("/admin/register_student", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

// export const registerLecturer = async (lecturerData: Lecturer) => {
//   const token = localStorage.getItem("token");
//   const response = await api.post("/admin/register_lecturer", lecturerData, {
//     headers: {
//       Authorization: `Bearer ${token}`,
//       "Content-Type": "application/json",
//     },
//   });
//   return response.data;
// };

export const fetchTeacherDashboardData = async () => {
  const response = await api.get("/teacher/dashboard", {
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
  });
  return response.data;
};

export const endAllTeacherSessions = async () => {
  const response = await api.post(
    "/teacher/end_all_sessions",
    {},
    {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    }
  );
  return response.data;
};

export const fetchAdminDashboardData =
  async (): Promise<AdminDashboardData> => {
    const response = await api.get("/admin/dashboard", {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    });
    return response.data;
  };

export const registerLecturer = async (
  name: string,
  email: string,
  password: string
): Promise<void> => {
  const response = await api.post(
    "/admin/register_lecturer",
    { name, email, password },
    {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    }
  );
  return response.data;
};

export const addCourse = async (
  courseName: string,
  lecturerId: string
): Promise<void> => {
  const response = await api.post(
    "/admin/add_course",
    { course_name: courseName, lecturer_id: lecturerId },
    {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    }
  );
  return response.data;
};

export const addTimetableEntry = async (
  courseId: string,
  day: string,
  startTime: string,
  endTime: string
): Promise<void> => {
  const response = await api.post(
    "/admin/add_timetable",
    { course_id: courseId, day, start_time: startTime, end_time: endTime },
    {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    }
  );
  return response.data;
};

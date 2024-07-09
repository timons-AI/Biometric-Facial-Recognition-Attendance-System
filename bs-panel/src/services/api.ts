import axios from "axios";
import { AdminDashboardData } from "../pages/admin/Dashboard";
import { ActiveSession } from "../pages/student/StartSession";
import { DashboardData } from "../pages/student/Dashboard";

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
  password: string;
}

interface Lecturer {
  name: string;
  email: string;
  password: string;
}

export interface LoginResponse {
  student_id: string;
  name: string;
  access_token: string;
}
export interface SessionResponse {
  message: string;
  session_id: string;
  qr_code: string;
}

export interface Course {
  id: string;
  name: string;
}

export const registerStudent = async (studentData: Student, images: File[]) => {
  const formData = new FormData();
  formData.append("student_id", studentData.student_id);
  formData.append("name", studentData.name);
  formData.append("email", studentData.email);
  formData.append("password", studentData.password); // Add this line
  images.forEach((image, index) => {
    formData.append("files", image, `face_${index}.jpg`);
  });

  const response = await api.post("/admin/register_student", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

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

export const studentLogin = async (
  email: string,
  password: string
): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>("/student/login", {
    email,
    password,
  });
  return response.data;
};

export const getStudentCourses = async (): Promise<Course[]> => {
  const response = await api.get<Course[]>("/student/courses");
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

export const getTimetable = async (courseId: string): Promise<any[]> => {
  const response = await api.get(`/timetable/${courseId}`);
  return response.data;
};

export const fetchStudentDashboardData = async (): Promise<DashboardData> => {
  const response = await api.get("/student/dashboard");
  return response.data;
};

// In api.ts

export const getActiveCourses = async (): Promise<Course[]> => {
  const response = await api.get<Course[]>("/student/active_courses");
  return response.data;
};

export const checkActiveSession = async (): Promise<ActiveSession | null> => {
  const response = await api.get("/student/active_session");
  return response.data;
};

export const startStudentSession = async (
  courseId: string,
  imageData: string
): Promise<SessionResponse> => {
  const response = await api.post<SessionResponse>("/student/start_session", {
    course_id: courseId,
    image: imageData,
  });
  return response.data;
};

export const endStudentSession = async (sessionId: string): Promise<void> => {
  const response = await api.post(`/student/end_session/${sessionId}`);
  return response.data;
};

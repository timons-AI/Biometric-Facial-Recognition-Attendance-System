import axios from "axios";
import { jwtDecode } from "jwt-decode";
import { Course } from "../timetable";
import { PaginatedResponse } from "../components/AdminApproval";

const API_URL = "http://localhost:5000/api";
//  https://421e-41-210-141-191.ngrok-free.app/api
// const API_URL = "https://421e-41-210-141-191.ngrok-free.app/api";

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

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export interface UserData {
  id: string;
  email: string;
  role: "student" | "lecturer" | "admin";
  name: string;
}

export const login = async (
  email: string,
  password: string
): Promise<UserData> => {
  const response = await api.post("/login", { email, password });
  const { access_token } = response.data;
  localStorage.setItem("token", access_token);

  const decodedToken = jwtDecode<UserData & { exp: number }>(access_token);
  console.log("Decoded Token:", decodedToken);

  if (
    !decodedToken.id ||
    !decodedToken.email ||
    !decodedToken.role ||
    !decodedToken.name
  ) {
    throw new Error("Invalid token payload");
  }

  return {
    id: decodedToken.id,
    email: decodedToken.email,
    role: decodedToken.role as "student" | "lecturer" | "admin",
    name: decodedToken.name,
  };
};

export const register = async (userData: FormData): Promise<void> => {
  const response = await api.post("/register", userData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export const registerAdmin = async (adminData: any) => {
  const response = await api.post("/register/admin", adminData);
  return response.data;
};

export const getPendingRegistrations = async (
  page: number = 1,
  perPage: number = 10
): Promise<PaginatedResponse> => {
  const response = await api.get(
    `/admin/pending_registrations?page=${page}&per_page=${perPage}`
  );
  return response.data;
};

export const approveUser = async (userId: number) => {
  const response = await api.post(`/admin/approve_user/${userId}`);
  return response.data;
};

export const rejectUser = async (userId: number) => {
  const response = await api.post(`/admin/reject_user/${userId}`);
  return response.data;
};
export const getLecturerTimetable = async (): Promise<Course[]> => {
  const response = await api.get("/api/lecturer/timetable");
  return response.data;
};

// export the api
export default api;

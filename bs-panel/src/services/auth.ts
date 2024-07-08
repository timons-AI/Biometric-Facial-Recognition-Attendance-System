import api from "./api";

export const loginStudent = async (faceId: string) => {
  const response = await api.post("/student/login", { faceId });
  return response.data;
};

export const loginLecturer = async (email: string, password: string) => {
  try {
    const response = await api.post("/lecturer/login", { email, password });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const loginAdmin = async (email: string, password: string) => {
  try {
    const response = await api.post("/admin/login", { email, password });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
};

import axios from "axios";

const API_URL = "http://localhost:5000/api";

export const registerStudent = async (
  name: string,
  studentId: string,
  images: File[]
) => {
  const formData = new FormData();
  formData.append("name", name);
  formData.append("student_id", studentId);
  images.forEach((image, index) => {
    formData.append(`files`, image, `face_${index}.jpg`);
  });

  const response = await axios.post(`${API_URL}/register`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const recognizeStudent = async (image: File) => {
  const formData = new FormData();
  formData.append("file", image);

  const response = await axios.post(`${API_URL}/recognize`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const getAttendance = async () => {
  const response = await axios.get(`${API_URL}/attendance`);
  return response.data;
};

export const getStudents = async () => {
  const response = await axios.get(`${API_URL}/students`);
  return response.data;
};

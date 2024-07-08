import axios from "axios";
import { Student } from "../components/StudentRegistration";

const API_URL = "http://localhost:5000/api";

export const registerStudent = async (student: Student, images: File[]) => {
  const formData = new FormData();

  // Append student data
  formData.append("name", `${student.firstName} ${student.lastName}`);
  formData.append("student_id", student.studentId);

  // Append additional student data
  formData.append("email", student.email);
  formData.append("password", student.password);
  formData.append("academic_year", student.academicYear.toString());
  formData.append("semester", student.semester);
  formData.append("academic_type", student.academicType);
  formData.append("academic_group", student.academicGroup);
  // formData.append("files", images[0], `face_0.jpg`);
  // log the number of images
  console.log(`Number of images: ${images.length}`);

  // Append images
  images.forEach((image, index) => {
    formData.append("files", image, `face_${index}.jpg`);
    console.log(`Appended image: ${image.name}, size: ${image.size} bytes`);
    console.log(`Appended image: ${image.name}, size: ${image.size} bytes`);
  });
  // Log the FormData contents
  for (let [key, value] of formData.entries()) {
    console.log(`${key}: ${value}`);
  }

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

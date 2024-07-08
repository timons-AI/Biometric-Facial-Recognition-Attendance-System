export interface Student {
  id: number;
  name: string;
  student_id: string;
}

export interface AttendanceRecord {
  id: number;
  student_id: number;
  check_in: string;
}

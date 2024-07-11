export interface CourseUnit {
  id: number;
  code: string;
  name: string;
}

export interface TimetableEntry {
  id: number;
  day: string;
  startTime: string;
  endTime: string;
  room: string;
  courseUnit: CourseUnit;
}

export interface Course {
  id: number;
  name: string;
  timetableEntries: TimetableEntry[];
}

import React, { useState } from "react";
import {
  Button,
  FormGroup,
  InputGroup,
  Intent,
  Card,
  MenuItem,
} from "@blueprintjs/core";
import { Select } from "@blueprintjs/select";

export interface Student {
  id?: number;
  firstName: string;
  lastName: string;
  email: string;
  studentId: string;
  password: string;
  academicYear: number;
  semester: "sem 1" | "sem 2";
  academicType: "teaching" | "tests" | "examination" | "recess term";
  academicGroup: string;
}

interface StudentRegistrationFormProps {
  onSubmit: (data: Student) => void;
  initialData?: Partial<Student>;
}

const academicYears = [2024, 2025, 2026, 2027];
const semesters: Array<"sem 1" | "sem 2"> = ["sem 1", "sem 2"];
const academicTypes: Array<
  "teaching" | "tests" | "examination" | "recess term"
> = ["teaching", "tests", "examination", "recess term"];
const academicGroups = ["Group A", "Group B", "Group C", "Group D"];

const StudentRegistrationForm: React.FC<StudentRegistrationFormProps> = ({
  onSubmit,
  initialData = {},
}) => {
  const [formData, setFormData] = useState<Student>({
    firstName: initialData.firstName || "",
    lastName: initialData.lastName || "",
    email: initialData.email || "",
    password: initialData.password || "",
    academicYear: initialData.academicYear || academicYears[0],
    semester: initialData.semester || semesters[0],
    studentId: initialData.studentId || "",
    academicType: initialData.academicType || academicTypes[0],
    academicGroup: initialData.academicGroup || academicGroups[0],
    ...initialData,
  });

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSelectChange = (field: keyof Student) => (value: any) => {
    setFormData((prevData) => ({
      ...prevData,
      [field]: value,
    }));
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit(formData);
  };

  const renderSelectItem = (item: any, { handleClick }: any) => (
    <MenuItem text={item} onClick={handleClick} roleStructure="listoption" />
  );

  return (
    <Card>
      <form onSubmit={handleSubmit}>
        <FormGroup
          label="First Name"
          labelFor="firstName-input"
          labelInfo="(required)"
        >
          <InputGroup
            id="firstName-input"
            name="firstName"
            placeholder="Enter first name"
            value={formData.firstName}
            onChange={handleInputChange}
            intent={Intent.PRIMARY}
          />
        </FormGroup>
        <FormGroup
          label="Last Name"
          labelFor="lastName-input"
          labelInfo="(required)"
        >
          <InputGroup
            id="lastName-input"
            name="lastName"
            placeholder="Enter last name"
            value={formData.lastName}
            onChange={handleInputChange}
            intent={Intent.PRIMARY}
          />
        </FormGroup>
        <FormGroup
          label="Student ID"
          labelFor="studentId-input"
          labelInfo="(required)"
        >
          <InputGroup
            id="studentId-input"
            name="studentId"
            placeholder="Enter student ID"
            value={formData.studentId}
            onChange={handleInputChange}
            intent={Intent.PRIMARY}
          />
        </FormGroup>
        <FormGroup label="Email" labelFor="email-input" labelInfo="(required)">
          <InputGroup
            id="email-input"
            name="email"
            placeholder="Enter email address"
            value={formData.email}
            onChange={handleInputChange}
            intent={Intent.PRIMARY}
            type="email"
          />
        </FormGroup>
        <FormGroup
          label="Password"
          labelFor="password-input"
          labelInfo="(required)"
        >
          <InputGroup
            id="password-input"
            name="password"
            placeholder="Enter password"
            value={formData.password}
            onChange={handleInputChange}
            intent={Intent.PRIMARY}
            type="password"
          />
        </FormGroup>
        <FormGroup label="Academic Year" labelFor="academicYear-select">
          <Select
            items={academicYears}
            itemRenderer={renderSelectItem}
            onItemSelect={handleSelectChange("academicYear")}
            filterable={false}
          >
            <Button
              text={formData.academicYear}
              rightIcon="double-caret-vertical"
            />
          </Select>
        </FormGroup>
        <FormGroup label="Semester" labelFor="semester-select">
          <Select
            items={semesters}
            itemRenderer={renderSelectItem}
            onItemSelect={handleSelectChange("semester")}
            filterable={false}
          >
            <Button
              text={formData.semester}
              rightIcon="double-caret-vertical"
            />
          </Select>
        </FormGroup>
        <FormGroup label="Academic Type" labelFor="academicType-select">
          <Select
            items={academicTypes}
            itemRenderer={renderSelectItem}
            onItemSelect={handleSelectChange("academicType")}
            filterable={false}
          >
            <Button
              text={formData.academicType}
              rightIcon="double-caret-vertical"
            />
          </Select>
        </FormGroup>
        <FormGroup label="Academic Group" labelFor="academicGroup-select">
          <Select
            items={academicGroups}
            itemRenderer={renderSelectItem}
            onItemSelect={handleSelectChange("academicGroup")}
            filterable={false}
          >
            <Button
              text={formData.academicGroup}
              rightIcon="double-caret-vertical"
            />
          </Select>
        </FormGroup>
        <Button type="submit" intent={Intent.PRIMARY} text="Register Student" />
      </form>
    </Card>
  );
};

export default StudentRegistrationForm;

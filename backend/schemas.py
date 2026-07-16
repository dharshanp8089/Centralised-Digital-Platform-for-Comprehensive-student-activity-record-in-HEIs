from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# ----------------- Authentication & User -----------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: EmailStr
    role: str
    name: str

class RegisterStudentRequest(BaseModel):
    email: EmailStr
    password: str
    roll_number: str
    name: str
    department_id: int
    semester: int = Field(default=1, ge=1, le=8)
    phone: Optional[str] = None

class RegisterFacultyRequest(BaseModel):
    email: EmailStr
    password: str
    faculty_id: str
    name: str
    department_id: int
    designation: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Department -----------------

class DepartmentBase(BaseModel):
    name: str
    code: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentOut(DepartmentBase):
    id: int

    class Config:
        from_attributes = True

# ----------------- Student -----------------

class StudentBase(BaseModel):
    roll_number: str
    name: str
    semester: int
    phone: Optional[str] = None
    cgpa: Decimal
    attendance_percentage: Decimal

class StudentUpdate(BaseModel):
    phone: Optional[str] = None
    semester: Optional[int] = Field(None, ge=1, le=8)
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)

class StudentOut(StudentBase):
    id: int
    user_id: int
    department_id: Optional[int] = None

    class Config:
        from_attributes = True

class StudentProfileOut(BaseModel):
    id: int
    roll_number: str
    name: str
    email: str
    department_name: Optional[str] = None
    department_code: Optional[str] = None
    semester: int
    phone: Optional[str] = None
    cgpa: float
    attendance_percentage: float

    class Config:
        from_attributes = True

# ----------------- Faculty -----------------

class FacultyBase(BaseModel):
    faculty_id: str
    name: str
    designation: Optional[str] = None

class FacultyOut(FacultyBase):
    id: int
    user_id: int
    department_id: Optional[int] = None
    department_name: Optional[str] = None

    class Config:
        from_attributes = True

# ----------------- Activity -----------------

# Note: Activity creation uses form-data due to file upload, but we define an output schema.
class ActivityOut(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    student_roll: Optional[str] = None
    title: str
    category: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str
    certificate_url: Optional[str] = None
    verified_by: Optional[int] = None
    verifier_name: Optional[str] = None
    verification_date: Optional[datetime] = None
    rejection_comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ActivityVerify(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    rejection_comment: Optional[str] = None

# ----------------- Attendance -----------------

class AttendanceRecord(BaseModel):
    student_id: int
    status: str = Field(..., pattern="^(present|absent|late)$")

class AttendanceBulkCreate(BaseModel):
    date: date
    records: List[AttendanceRecord]

class AttendanceOut(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    student_roll: Optional[str] = None
    date: date
    status: str
    marked_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Dashboard & Analytics -----------------

class CategoryCount(BaseModel):
    category: str
    count: int

class DepartmentCount(BaseModel):
    department: str
    code: str
    student_count: int

class DashboardStats(BaseModel):
    total_students: int
    total_faculty: int
    total_activities: int
    pending_activities: int
    approved_activities: int
    rejected_activities: int
    average_attendance: float
    category_breakdown: List[CategoryCount]
    department_distribution: List[DepartmentCount]

# ----------------- Announcements -----------------

class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    content: str = Field(..., min_length=5)
    department_id: Optional[int] = None

class AnnouncementOut(BaseModel):
    id: int
    title: str
    content: str
    created_by: str
    created_at: datetime
    department_id: Optional[int] = None
    department_code: Optional[str] = None

    class Config:
        from_attributes = True


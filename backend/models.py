from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False)

    # Relationships
    students = relationship("Student", back_populates="department")
    faculty = relationship("Faculty", back_populates="department")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'admin', 'faculty', 'student'
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    student = relationship("Student", uselist=False, back_populates="user", cascade="all, delete-orphan")
    faculty = relationship("Faculty", uselist=False, back_populates="user", cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    roll_number = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"))
    semester = Column(Integer, default=1)
    phone = Column(String(20))
    cgpa = Column(Numeric(4, 2), default=0.00)
    attendance_percentage = Column(Numeric(5, 2), default=100.00)

    # Relationships
    user = relationship("User", back_populates="student")
    department = relationship("Department", back_populates="students")
    activities = relationship("Activity", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")

class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    faculty_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"))
    designation = Column(String(100))

    # Relationships
    user = relationship("User", back_populates="faculty")
    department = relationship("Department", back_populates="faculty")
    marked_attendances = relationship("Attendance", back_populates="marker")
    verified_activities = relationship("Activity", back_populates="verifier")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)  # 'internship', 'project', 'certification', 'extracurricular', 'placement'
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(20), default="pending")  # 'pending', 'approved', 'rejected'
    certificate_url = Column(String(255))  # Path to stored file
    verified_by = Column(Integer, ForeignKey("faculty.id", ondelete="SET NULL"))
    verification_date = Column(DateTime)
    rejection_comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="activities")
    verifier = relationship("Faculty", back_populates="verified_activities")

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(10), nullable=False)  # 'present', 'absent', 'late'
    marked_by = Column(Integer, ForeignKey("faculty.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    marker = relationship("Faculty", back_populates="marked_attendances")

    # Constraints
    __table_args__ = (UniqueConstraint('student_id', 'date', name='unique_student_date'),)

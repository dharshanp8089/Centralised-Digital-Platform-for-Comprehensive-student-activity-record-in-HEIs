-- Centralised Digital Platform for Comprehensive Student Activity Record in HEIs
-- PostgreSQL Database Schema

-- Enable UUID extension if needed (optional)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop tables if they exist (for easy re-initialization)
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS activities CASCADE;
DROP TABLE IF EXISTS faculty CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- 1. Departments Table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL
);

-- 2. Users Table (Core authentication)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'faculty', 'student')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Students Table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    roll_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    semester INTEGER NOT NULL DEFAULT 1 CHECK (semester BETWEEN 1 AND 8),
    phone VARCHAR(20),
    cgpa NUMERIC(4,2) DEFAULT 0.00 CHECK (cgpa BETWEEN 0.00 AND 10.00),
    attendance_percentage NUMERIC(5,2) DEFAULT 100.00 CHECK (attendance_percentage BETWEEN 0.00 AND 100.00)
);

-- 4. Faculty Table
CREATE TABLE faculty (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    faculty_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    designation VARCHAR(100)
);

-- 5. Activities Table
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('internship', 'project', 'certification', 'extracurricular', 'placement')),
    description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    certificate_url VARCHAR(255),
    verified_by INTEGER REFERENCES faculty(id) ON DELETE SET NULL,
    verification_date TIMESTAMP,
    rejection_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Attendance Table
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('present', 'absent', 'late')),
    marked_by INTEGER REFERENCES faculty(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_student_date UNIQUE(student_id, date)
);

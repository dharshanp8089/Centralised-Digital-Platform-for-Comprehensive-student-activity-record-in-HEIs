# Centralised Digital Platform for Comprehensive Student Activity Record in HEIs

A premium, secure web application designed for Higher Education Institutions (HEIs) to manage and verify student co-curricular achievements, projects, certifications, and attendance logs.

---

## 📊 Project Overview & Architecture

This system provides Higher Education Institutions with a unified, role-based database to record and verify co-curricular and extra-curricular achievements. 

```
                                  +-----------------------+
                                  |   Web Browser Client   |
                                  | (HTML5/CSS3/Vanilla JS) |
                                  +-----------+-----------+
                                              |
                                              | (AJAX + JWT Auth)
                                              v
                                  +-----------+-----------+
                                  |      FastAPI Server    |
                                  |     (Backend Router)  |
                                  +-----------+-----------+
                                              |
                                              | (SQLAlchemy ORM)
                                              v
                                  +-----------+-----------+
                                  |   PostgreSQL Database  |
                                  |  (Student/Faculty DB) |
                                  +-----------------------+
```

---

## ✨ Features

### 👤 Role-Based Portals

#### 🎓 Student Portal
*   **Profile Analytics**: Visual glassmorphism progress wheels for Cumulative GPA (CGPA) and attendance rate.
*   **Activity Logs**: View certifications, internships, projects, extracurriculars, and placement records as premium interactive tiles.
*   **Integrated Certificate Viewer**: Upload and view certificate documents (PDFs/Images) in a secure modal window.
*   **Attendance logs**: GitHub-style visual contribution heatmap calendar grid of daily color-coded attendance tiles (Present, Absent, Late) with hover micro-animations.
*   **Announcements bulletins widget**: Stay updated with global notice feeds and target departmental notices.
*   **Profile Settings**: Dynamically update phone number, current semester, and CGPA.

#### 🏫 Faculty Portal
*   **Verification Queue**: Audit and approve/reject student certificate submissions with rejection comments.
*   **Announcements Broadcast**: Create and target departmental notice broadcasts.
*   **Student Registry**: Lists all department students, highlighting low attendance rates.
*   **Interactive Roster Logger**: Mark daily student attendance as Present (P), Absent (A), or Late (L) for any selected date, triggering dynamic percentage recalculation.

#### ⚙️ Administrator Portal
*   **Analytical Dashboard**: Live stats overview and interactive charts (Doughnut chart for category distribution, Bar chart for department student counts).
*   **Announcements Broadcaster**: Create and target global institutional notifications.
*   **User Directory**: Search, review, and delete student, faculty, and administrative accounts.
*   **Departments Registry**: Register and manage academic departments.
*   **CSV Reports**: Generate and download structured reports of student records.
*   **Secure Backups**: Perform database exports as structured JSON snapshots.

---

## 🛠️ Technology Stack
*   **Backend**: Python, FastAPI, Uvicorn, SQLAlchemy, PostgreSQL, JWT Authentication.
*   **Frontend**: Vanilla HTML5, CSS3, Javascript, Chart.js, Bootstrap 5.

---

## 🔒 Default Role Credentials

You can test all portals using the pre-seeded default accounts below:

| Role | Username | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin@hei.edu` | `adminpassword` |
| **Faculty Member** | `faculty@hei.edu` | `facultypassword` |
| **Student** | `student@hei.edu` | `studentpassword` |

---

## 🚀 Installation & Local Setup

### 1. Prerequisites
Ensure you have python and PostgreSQL installed. Create a database named `student_db`:
```sql
CREATE DATABASE student_db;
```

### 2. Configure Environment `.env`
Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL=postgresql://postgres:<your_password>@localhost:5432/student_db
JWT_SECRET=9a4f8e6c2d1b8a5f3c7e0b2a1f4e5d6c8b9a0f1e2d3c4b5a6f7e8d9c0b1a2f3
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

### 3. Initialize & Seed Database
Build the schema tables and populate them with mock test data and announcements:
```powershell
.\venv\Scripts\python.exe backend/seed.py
```

### 4. Run the Servers (Single Command)
Double-click `start.bat` or run:
```powershell
.\start.bat
```
*   **Backend API**: http://localhost:8000
*   **Frontend Web Interface**: http://localhost:8000/

---

## 🧪 Integration Verification Tests
To run backend integration test suites checking access permissions, E2E student certificate uploads, faculty reviews, and attendance logging, run:
```powershell
.\venv\Scripts\python.exe backend/test_upgrades.py
.\venv\Scripts\python.exe backend/test_full_workflow.py
```

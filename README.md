# Centralised Digital Platform for Comprehensive Student Activity Record in HEIs

A premium, secure web application designed for Higher Education Institutions (HEIs) to manage and verify student co-curricular achievements, projects, certifications, and attendance logs.

---

## 📹 Demo Video / Walkthrough
*Place your demonstration video here to showcase the platform! (See instructions below on how to upload it)*

<!-- ADD_VIDEO_START -->
> [!TIP]
> **How to add your video here:**
> 1. Go to your repository on GitHub.com and click **Edit** (pencil icon) on this `README.md` file.
> 2. Drag and drop your video file (MP4, MOV, etc., up to 10MB) directly into this section of the editor.
> 3. GitHub will upload the video and automatically generate a video link (e.g., `https://github.com/user-attachments/assets/...`) which embeds a native video player right on the page!
<!-- ADD_VIDEO_END -->

---

## ✨ Features

### 👤 Role-Based Portals

#### 🎓 Student Portal
*   **Profile Analytics**: Visual glassmorphism progress wheels for Cumulative GPA (CGPA) and attendance rate.
*   **Activity Logs**: View certifications, internships, projects, extracurriculars, and placement records as premium interactive tiles.
*   **Integrated Certificate Viewer**: Upload and view certificate documents (PDFs/Images) in a secure modal window.
*   **Attendance logs**: Modern daily heat-map calendar of color-coded attendance tiles (Present, Absent, Late) with hover micro-animations.
*   **Profile Settings**: Dynamically update phone number, current semester, and CGPA.

#### 🏫 Faculty Portal
*   **Verification Queue**: Audit and approve/reject student certificate submissions with rejection comments.
*   **Student Registry**: Lists all department students, highlighting low attendance rates.
*   **Interactive Roster Logger**: Mark daily student attendance as Present (P), Absent (A), or Late (L) for any selected date.

#### ⚙️ Administrator Portal
*   **Analytical Dashboard**: Live stats overview and interactive charts (Doughnut chart for category distribution, Bar chart for department student counts).
*   **User Directory**: Search, review, and delete student, faculty, and administrative accounts.
*   **Departments Registry**: Register and manage academic departments.
*   **CSV Reports**: Generate and download structured reports of student records.
*   **Secure Backups**: Perform database exports as structured JSON snapshots.

---

## 🛠️ Technology Stack
*   **Backend**: Python, FastAPI, Uvicorn, SQLAlchemy, PostgreSQL, JWT Authentication.
*   **Frontend**: Vanilla HTML5, CSS3, Javascript, Chart.js, Bootstrap 5.

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
JWT_SECRET=<your_jwt_secret_key>
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

### 3. Initialize & Seed Database
Build the schema tables and populate them with mock test data:
```powershell
.\venv\Scripts\python.exe backend/seed.py
```

### 4. Run the Servers (Single Command)
Double-click `start.bat` or run:
```powershell
.\start.bat
```
*   **Backend API**: http://localhost:8000
*   **Frontend Server**: http://localhost:5500

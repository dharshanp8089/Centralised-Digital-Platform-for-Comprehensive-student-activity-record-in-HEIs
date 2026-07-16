import os
import sys
from datetime import datetime, date, timedelta
from sqlalchemy import text
from dotenv import load_dotenv

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine, Base
from backend import models
from backend.auth import hash_password

load_dotenv()

def run_sql_schema():
    print("--- Reading schema.sql ---")
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "schema.sql")
    if not os.path.exists(schema_path):
        print(f"Error: schema.sql not found at {schema_path}")
        return False
    
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    
    # Connect and execute schema
    print("--- Initializing Database Tables via Schema SQL ---")
    db = SessionLocal()
    try:
        # Split sql by semicolons or run as block.
        # Since PostgreSQL can execute multiple statements in one block, we can use text()
        db.execute(text(schema_sql))
        db.commit()
        print("Schema SQL executed successfully.")
        return True
    except Exception as e:
        db.rollback()
        print("Error executing schema SQL:")
        print(e)
        print("\nIMPORTANT: Make sure your PostgreSQL server is running and the database 'student_db' exists.")
        print("You can create it by running in psql: CREATE DATABASE student_db;")
        return False
    finally:
        db.close()

def seed_data():
    print("--- Seeding Database Content ---")
    db = SessionLocal()
    try:
        # 1. Seed Departments
        departments_data = [
            {"name": "Computer Science & Engineering", "code": "CSE"},
            {"name": "Electronics & Communication Engineering", "code": "ECE"},
            {"name": "Electrical & Electronics Engineering", "code": "EEE"},
            {"name": "Mechanical Engineering", "code": "ME"},
            {"name": "Civil Engineering", "code": "CE"}
        ]
        
        departments = []
        for dept in departments_data:
            d = models.Department(name=dept["name"], code=dept["code"])
            db.add(d)
            departments.append(d)
        db.flush() # get generated IDs
        
        dept_map = {d.code: d for d in departments}
        print(f"Seeded {len(departments)} departments.")

        # 2. Seed Admin User
        admin_user = models.User(
            email="admin@hei.edu",
            password_hash=hash_password("adminpassword"),
            role="admin"
        )
        db.add(admin_user)
        print("Seeded Admin user (admin@hei.edu / adminpassword).")

        # 3. Seed Faculty Users & Profiles
        faculty_users_data = [
            {
                "email": "faculty@hei.edu",
                "password": "facultypassword",
                "faculty_id": "F001",
                "name": "Dr. Sarah Connor",
                "dept_code": "CSE",
                "designation": "Associate Professor"
            },
            {
                "email": "faculty_ece@hei.edu",
                "password": "facultypassword",
                "faculty_id": "F002",
                "name": "Dr. Alan Turing",
                "dept_code": "ECE",
                "designation": "Professor & Head"
            }
        ]

        faculty_profiles = []
        for fac in faculty_users_data:
            user = models.User(
                email=fac["email"],
                password_hash=hash_password(fac["password"]),
                role="faculty"
            )
            db.add(user)
            db.flush()
            
            profile = models.Faculty(
                user_id=user.id,
                faculty_id=fac["faculty_id"],
                name=fac["name"],
                department_id=dept_map[fac["dept_code"]].id,
                designation=fac["designation"]
            )
            db.add(profile)
            faculty_profiles.append(profile)
        db.flush()
        print(f"Seeded {len(faculty_profiles)} faculty profiles.")

        # 4. Seed Student Users & Profiles
        student_users_data = [
            {
                "email": "student@hei.edu",
                "password": "studentpassword",
                "roll_number": "S101",
                "name": "John Doe",
                "dept_code": "CSE",
                "semester": 6,
                "phone": "+91 9876543210",
                "cgpa": 8.75,
                "attendance_percentage": 92.50
            },
            {
                "email": "alice@hei.edu",
                "password": "studentpassword",
                "roll_number": "S102",
                "name": "Alice Smith",
                "dept_code": "ECE",
                "semester": 4,
                "phone": "+91 9876543211",
                "cgpa": 9.10,
                "attendance_percentage": 96.00
            },
            {
                "email": "bob@hei.edu",
                "password": "studentpassword",
                "roll_number": "S103",
                "name": "Bob Johnson",
                "dept_code": "CSE",
                "semester": 6,
                "phone": "+91 9876543212",
                "cgpa": 7.20,
                "attendance_percentage": 78.40
            },
            {
                "email": "charlie@hei.edu",
                "password": "studentpassword",
                "roll_number": "S104",
                "name": "Charlie Brown",
                "dept_code": "ME",
                "semester": 8,
                "phone": "+91 9876543213",
                "cgpa": 6.80,
                "attendance_percentage": 85.00
            }
        ]

        students = []
        for stud in student_users_data:
            user = models.User(
                email=stud["email"],
                password_hash=hash_password(stud["password"]),
                role="student"
            )
            db.add(user)
            db.flush()
            
            profile = models.Student(
                user_id=user.id,
                roll_number=stud["roll_number"],
                name=stud["name"],
                department_id=dept_map[stud["dept_code"]].id,
                semester=stud["semester"],
                phone=stud["phone"],
                cgpa=stud["cgpa"],
                attendance_percentage=stud["attendance_percentage"]
            )
            db.add(profile)
            students.append(profile)
        db.flush()
        
        student_map = {s.roll_number: s for s in students}
        print(f"Seeded {len(students)} student profiles.")

        # 5. Seed Activities (Certifications, internships, projects)
        f_cse_id = faculty_profiles[0].id
        f_ece_id = faculty_profiles[1].id
        
        activities_data = [
            # John Doe CSE
            {
                "roll": "S101",
                "title": "Summer Web Developer Internship at Google",
                "category": "internship",
                "description": "Completed a 2-month summer internship working with Google Cloud Platform and backend APIs.",
                "start_date": date(2025, 5, 1),
                "end_date": date(2025, 6, 30),
                "status": "approved",
                "certificate_url": "/uploads/google_internship.pdf",
                "verified_by": f_cse_id,
                "verification_date": datetime.now() - timedelta(days=10)
            },
            {
                "roll": "S101",
                "title": "AWS Certified Developer Associate",
                "category": "certification",
                "description": "Validation of technical expertise in developing and maintaining applications on AWS.",
                "start_date": date(2025, 10, 15),
                "end_date": date(2028, 10, 15),
                "status": "approved",
                "certificate_url": "/uploads/aws_cert.pdf",
                "verified_by": f_cse_id,
                "verification_date": datetime.now() - timedelta(days=5)
            },
            {
                "roll": "S101",
                "title": "IoT Smart Agriculture Irrigation System",
                "category": "project",
                "description": "Designed and coded an automated irrigation framework using Arduino, NodeMCU, and soil moisture sensors.",
                "start_date": date(2026, 1, 10),
                "end_date": date(2026, 4, 20),
                "status": "pending",
                "certificate_url": "/uploads/iot_project.pdf",
                "verified_by": None,
                "verification_date": None
            },
            # Alice Smith ECE
            {
                "roll": "S102",
                "title": "High Frequency RFID Transceiver Design",
                "category": "project",
                "description": "Graduation design project analyzing impedance matching for high frequency antennas.",
                "start_date": date(2025, 8, 1),
                "end_date": date(2025, 11, 30),
                "status": "approved",
                "certificate_url": "/uploads/rfid_project.pdf",
                "verified_by": f_ece_id,
                "verification_date": datetime.now() - timedelta(days=12)
            },
            {
                "roll": "S102",
                "title": "National Level Hackathon Winner",
                "category": "extracurricular",
                "description": "Secured 1st place in Smart City Track hackathon organized by IIT Bombay.",
                "start_date": date(2026, 2, 10),
                "end_date": date(2026, 2, 12),
                "status": "pending",
                "certificate_url": "/uploads/hackathon_winner.pdf",
                "verified_by": None,
                "verification_date": None
            },
            # Bob Johnson CSE
            {
                "roll": "S103",
                "title": "React Native Mobile App for College Canteen",
                "category": "project",
                "description": "Created a hybrid app with digital payments using Stripe.",
                "start_date": date(2025, 9, 1),
                "end_date": date(2025, 12, 10),
                "status": "rejected",
                "certificate_url": "/uploads/canteen_app.pdf",
                "verified_by": f_cse_id,
                "verification_date": datetime.now() - timedelta(days=2),
                "rejection_comment": "Please upload a clearer certificate and a GitHub project link."
            }
        ]
        
        for act in activities_data:
            a = models.Activity(
                student_id=student_map[act["roll"]].id,
                title=act["title"],
                category=act["category"],
                description=act["description"],
                start_date=act["start_date"],
                end_date=act["end_date"],
                status=act["status"],
                certificate_url=act["certificate_url"],
                verified_by=act["verified_by"],
                verification_date=act["verification_date"],
                rejection_comment=act.get("rejection_comment")
            )
            db.add(a)
        db.flush()
        print(f"Seeded {len(activities_data)} student activities.")

        # 6. Seed Attendance Logs (last 5 class days)
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(5)]
        
        attendance_logs_count = 0
        for s in students:
            # S101, S102 have very high attendance. S103 has lower.
            for d in dates:
                if d.weekday() >= 5: # skip weekends
                    continue
                
                # Determine status
                if s.roll_number == "S103" and d.day % 3 == 0:
                    status = "absent"
                elif s.roll_number == "S104" and d.day % 4 == 0:
                    status = "absent"
                elif d.day % 7 == 0:
                    status = "late"
                else:
                    status = "present"
                
                att = models.Attendance(
                    student_id=s.id,
                    date=d,
                    status=status,
                    marked_by=f_cse_id if s.department.code == "CSE" else f_ece_id
                )
                db.add(att)
                attendance_logs_count += 1
        
        # 7. Seed Announcements
        announcements_data = [
            {
                "title": "Welcome to the Student Activity Portal!",
                "content": "Welcome to the newly launched centralized digital platform for co-curricular achievements and verification. Please upload all your certificates, internships, and placement records here.",
                "created_by": "Administrator",
                "department_id": None
            },
            {
                "title": "CSE Activity Submission Deadline",
                "content": "All Computer Science students must upload their project and internship documents before the upcoming Friday for review by the department heads.",
                "created_by": "Dr. Sarah Connor",
                "department_id": dept_map["CSE"].id
            },
            {
                "title": "ECE Certification Guidelines",
                "content": "Students submitting hardware course certifications must attach verifiable PDF transcripts matching the dates precisely.",
                "created_by": "Dr. Alan Turing",
                "department_id": dept_map["ECE"].id
            }
        ]

        for ann in announcements_data:
            a = models.Announcement(
                title=ann["title"],
                content=ann["content"],
                created_by=ann["created_by"],
                department_id=ann["department_id"]
            )
            db.add(a)

        db.commit()
        print(f"Seeded {len(announcements_data)} announcements.")
        print(f"Seeded {attendance_logs_count} attendance records.")
        print("--- Seeding Completed Successfully! ---")
        return True

    except Exception as e:
        db.rollback()
        print("Error during database seeding:")
        print(e)
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if run_sql_schema():
        seed_data()

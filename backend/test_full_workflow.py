import os
import sys
import random
from fastapi.testclient import TestClient

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.database import SessionLocal
from backend import models

client = TestClient(app)

def test_full_workflow():
    print("=== STARTING ADVANCED END-TO-END WORKFLOW TESTS ===")
    
    # 1. Login as Admin to set up department and faculty
    print("1. Admin Login...")
    login_response = client.post("/api/auth/login", json={
        "email": "admin@hei.edu",
        "password": "adminpassword"
    })
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Check if ECE department exists, or create a new one
    db = SessionLocal()
    ece_dept = db.query(models.Department).filter(models.Department.code == "ECE").first()
    if not ece_dept:
        print("Creating ECE Department...")
        dept_res = client.post("/api/admin/departments", headers=admin_headers, json={
            "name": "Electronics & Communication Engineering",
            "code": "ECE"
        })
        assert dept_res.status_code == 201
        dept_id = dept_res.json()["id"]
    else:
        dept_id = ece_dept.id
    db.close()
    
    # 2. Register a new Faculty for ECE
    fac_email = f"test_fac_{random.randint(100, 999)}@hei.edu"
    fac_id = f"TFAC-{random.randint(1000, 9999)}"
    print(f"2. Registering Faculty ({fac_email}, ID: {fac_id})...")
    fac_reg = client.post("/api/auth/register/faculty", json={
        "email": fac_email,
        "password": "facultypassword",
        "faculty_id": fac_id,
        "name": "Test Prof Logan",
        "department_id": dept_id,
        "designation": "Assistant Professor"
    })
    assert fac_reg.status_code == 201
    
    # 3. Register a new Student for ECE
    stud_email = f"test_stud_{random.randint(100, 999)}@hei.edu"
    stud_roll = f"TSTUD-{random.randint(1000, 9999)}"
    print(f"3. Registering Student ({stud_email}, Roll: {stud_roll})...")
    stud_reg = client.post("/api/auth/register/student", json={
        "email": stud_email,
        "password": "studentpassword",
        "roll_number": stud_roll,
        "name": "Test Student Bruce",
        "department_id": dept_id,
        "semester": 4,
        "phone": "+91 9999999999"
    })
    assert stud_reg.status_code == 201
    
    # 4. Login as the student
    print("4. Student Login...")
    stud_login = client.post("/api/auth/login", json={
        "email": stud_email,
        "password": "studentpassword"
    })
    assert stud_login.status_code == 200
    stud_token = stud_login.json()["access_token"]
    stud_headers = {"Authorization": f"Bearer {stud_token}"}
    
    # 5. Get Student Profile & Update Profile Settings
    print("5. Testing Profile retrieve and update...")
    prof_get = client.get("/api/students/profile", headers=stud_headers)
    assert prof_get.status_code == 200
    
    prof_update = client.put("/api/students/profile", headers=stud_headers, json={
        "phone": "+91 8888888888",
        "semester": 5,
        "cgpa": 9.35
    })
    assert prof_update.status_code == 200
    updated_data = prof_update.json()
    assert updated_data["phone"] == "+91 8888888888"
    assert updated_data["semester"] == 5
    assert updated_data["cgpa"] == 9.35
    print("Student profile update verified successfully.")
    
    # 6. Upload mock certificate activity
    print("6. Student uploading activity...")
    # Create a small dummy file
    dummy_file_path = "backend/dummy_cert.pdf"
    with open(dummy_file_path, "wb") as f:
        f.write(b"%PDF-1.4 Mock PDF certificate content")
        
    try:
        with open(dummy_file_path, "rb") as f:
            upload_res = client.post(
                "/api/students/activities",
                headers={"Authorization": f"Bearer {stud_token}"},
                data={
                    "title": "Machine Learning Specialization",
                    "category": "certification",
                    "description": "Completed Coursera ML specialization",
                    "start_date": "2026-05-01",
                    "end_date": "2026-05-31"
                },
                files={"file": ("dummy_cert.pdf", f, "application/pdf")}
            )
        assert upload_res.status_code == 200
        activity_id = upload_res.json()["id"]
        assert upload_res.json()["title"] == "Machine Learning Specialization"
        assert upload_res.json()["status"] == "pending"
        print(f"Activity upload verified successfully. Activity ID: {activity_id}")
    finally:
        if os.path.exists(dummy_file_path):
            os.remove(dummy_file_path)
            
    # 7. Login as Faculty
    print("7. Faculty Login...")
    fac_login = client.post("/api/auth/login", json={
        "email": fac_email,
        "password": "facultypassword"
    })
    assert fac_login.status_code == 200
    fac_token = fac_login.json()["access_token"]
    fac_headers = {"Authorization": f"Bearer {fac_token}"}
    
    # 8. Faculty retrieves students and pending activities
    print("8. Faculty checking department records...")
    dept_studs = client.get("/api/faculty/students", headers=fac_headers)
    assert dept_studs.status_code == 200
    assert len(dept_studs.json()) >= 1  # must see the new student
    
    pending_acts = client.get("/api/faculty/pending-activities", headers=fac_headers)
    assert pending_acts.status_code == 200
    pending_ids = [act["id"] for act in pending_acts.json()]
    assert activity_id in pending_ids
    print("Faculty successfully fetched students and identified pending activity.")
    
    # 9. Faculty verifies activity (Approve)
    print("9. Faculty verifying activity...")
    verify_res = client.post(
        f"/api/faculty/verify-activity/{activity_id}",
        headers=fac_headers,
        json={
            "status": "approved"
        }
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "approved"
    
    # Check that it's no longer in pending activities queue
    pending_acts_after = client.get("/api/faculty/pending-activities", headers=fac_headers)
    assert pending_acts_after.status_code == 200
    pending_ids_after = [act["id"] for act in pending_acts_after.json()]
    assert activity_id not in pending_ids_after
    print("Faculty verification (Approve) verified successfully.")
    
    # 10. Faculty logs attendance for student
    print("10. Faculty marking attendance...")
    att_res = client.post(
        "/api/faculty/attendance",
        headers=fac_headers,
        json={
            "date": "2026-07-13",
            "records": [
                {
                    "student_id": updated_data["id"],
                    "status": "absent"
                }
            ]
        }
    )
    assert att_res.status_code == 200
    
    # Check student attendance logs and updated attendance percentage
    stud_att = client.get("/api/students/attendance", headers=stud_headers)
    assert stud_att.status_code == 200
    att_records = stud_att.json()
    assert len(att_records) > 0
    # Find marked date
    marked = [r for r in att_records if r["date"] == "2026-07-13"]
    assert len(marked) == 1
    assert marked[0]["status"] == "absent"
    
    # Verify that attendance percentage is recalculated
    prof_after_att = client.get("/api/students/profile", headers=stud_headers)
    assert prof_after_att.status_code == 200
    percentage = prof_after_att.json()["attendance_percentage"]
    assert percentage < 100.0
    print(f"Recalculation of attendance percentage verified successfully. Current rate: {percentage}%")

    
    # 11. Cleanup E2E test users
    print("11. Cleaning up E2E records...")
    db = SessionLocal()
    try:
        # Delete student user
        stud_user = db.query(models.User).filter(models.User.email == stud_email).first()
        if stud_user:
            client.delete(f"/api/admin/users/{stud_user.id}", headers=admin_headers)
            
        # Delete faculty user
        fac_user = db.query(models.User).filter(models.User.email == fac_email).first()
        if fac_user:
            client.delete(f"/api/admin/users/{fac_user.id}", headers=admin_headers)
            
        print("Cleanup successful.")
    finally:
        db.close()
        
    print("=== ALL END-TO-END WORKFLOW TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    try:
        test_full_workflow()
    except Exception as e:
        print(f"Workflow test failed: {e}")
        sys.exit(1)

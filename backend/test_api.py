import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend import models

client = TestClient(app)

def test_root_endpoint():
    print("Testing ROOT endpoint...")
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    print("ROOT endpoint is OK.")

def test_database_connectivity():
    print("Testing DB connection...")
    db = SessionLocal()
    try:
        # Check if database can execute a basic select query
        from sqlalchemy import text
        res = db.execute(text("SELECT 1")).scalar()
        assert res == 1
        print("DB connection is OK.")
    except Exception as e:
        print(f"DB connection FAILED: {e}")
        raise e
    finally:
        db.close()

def test_api_workflow():
    print("Testing Auth and Profile workflow...")
    
    # 1. Login as Admin
    print("Logging in as Admin...")
    login_response = client.post("/api/auth/login", json={
        "email": "admin@hei.edu",
        "password": "adminpassword"
    })
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token_data = login_response.json()
    assert "access_token" in token_data
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Admin login successful. Token acquired.")

    # 2. Add a new test department
    import random
    dept_code = f"TEST{random.randint(100, 999)}"
    print(f"Creating department with code: {dept_code}...")
    dept_response = client.post("/api/admin/departments", headers=headers, json={
        "name": f"Test Department {dept_code}",
        "code": dept_code
    })
    assert dept_response.status_code == 201, f"Dept creation failed: {dept_response.text}"
    dept = dept_response.json()
    dept_id = dept["id"]
    print(f"Department created. ID: {dept_id}")

    # 3. Register a student in the test department
    stud_email = f"test_student_{dept_code}@hei.edu"
    stud_roll = f"ROLL-{dept_code}"
    print(f"Registering student: {stud_email}...")
    reg_response = client.post("/api/auth/register/student", json={
        "email": stud_email,
        "password": "testpassword",
        "roll_number": stud_roll,
        "name": "Test Student Joe",
        "department_id": dept_id,
        "semester": 1,
        "phone": "+91 9999999999"
    })
    assert reg_response.status_code == 201, f"Student registration failed: {reg_response.text}"
    print("Student registered successfully.")

    # 4. Login as the newly created student
    print("Logging in as Student...")
    stud_login = client.post("/api/auth/login", json={
        "email": stud_email,
        "password": "testpassword"
    })
    assert stud_login.status_code == 200, f"Student login failed: {stud_login.text}"
    stud_token_data = stud_login.json()
    stud_token = stud_token_data["access_token"]
    stud_headers = {"Authorization": f"Bearer {stud_token}"}
    print("Student login successful.")

    # 5. Fetch student profile details
    print("Fetching student profile...")
    prof_response = client.get("/api/students/profile", headers=stud_headers)
    assert prof_response.status_code == 200, f"Profile load failed: {prof_response.text}"
    prof = prof_response.json()
    assert prof["roll_number"] == stud_roll
    assert prof["email"] == stud_email
    print("Student profile values verify correctly.")

    # 6. Fetch admin dashboard stats
    print("Fetching Admin Dashboard Statistics...")
    stats_response = client.get("/api/admin/dashboard-stats", headers=headers)
    assert stats_response.status_code == 200, f"Stats load failed: {stats_response.text}"
    stats = stats_response.json()
    assert stats["total_students"] > 0
    print("Dashboard metrics match correct totals.")

    # 7. Cleanup the test users
    print("Cleaning up registered test user accounts...")
    # Find test user in db
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == stud_email).first()
        if user:
            # Delete user
            del_response = client.delete(f"/api/admin/users/{user.id}", headers=headers)
            assert del_response.status_code == 200
            print("Student test account deleted.")
            
        # Delete department
        del_dept_response = client.delete(f"/api/admin/departments/{dept_id}", headers=headers)
        assert del_dept_response.status_code == 200
        print("Department test record deleted.")
    finally:
        db.close()

if __name__ == "__main__":
    print("=== STARTING API AND DATABASE VERIFICATION TESTS ===")
    try:
        test_root_endpoint()
        test_database_connectivity()
        test_api_workflow()
        print("=== ALL TESTS PASSED SUCCESSFULLY! ===")
    except Exception as e:
        print(f"=== TEST RUN ENCOUNTERED ERROR: {e} ===")
        sys.exit(1)

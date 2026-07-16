import os
import sys
from fastapi.testclient import TestClient

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.database import SessionLocal
from backend import models

client = TestClient(app)

def test_announcements_flow():
    print("=== STARTING INTEGRATION TESTS FOR ANNOUNCEMENTS UPGRADE ===")

    # 1. Admin Login
    print("1. Admin logging in...")
    admin_login = client.post("/api/auth/login", json={
        "email": "admin@hei.edu",
        "password": "adminpassword"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Fetch departments
    db = SessionLocal()
    cse_dept = db.query(models.Department).filter(models.Department.code == "CSE").first()
    ece_dept = db.query(models.Department).filter(models.Department.code == "ECE").first()
    assert cse_dept is not None
    assert ece_dept is not None
    db.close()

    # 2. Student Login (CSE)
    print("2. Student logging in...")
    student_login = client.post("/api/auth/login", json={
        "email": "student@hei.edu",
        "password": "studentpassword"
    })
    assert student_login.status_code == 200
    stud_token = student_login.json()["access_token"]
    stud_headers = {"Authorization": f"Bearer {stud_token}"}

    # 3. Try posting announcement as Student (should fail)
    print("3. Testing role permissions (Student posting)...")
    fail_post = client.post(
        "/api/announcements",
        headers=stud_headers,
        json={
            "title": "Hackathon announcement",
            "content": "Hackathon registrations open today!",
            "department_id": None
        }
    )
    assert fail_post.status_code == 403
    print("Security role check passed: Student cannot post announcements.")

    # 4. Post announcement as Admin (Global)
    print("4. Posting Global announcement as Admin...")
    global_ann = client.post(
        "/api/announcements",
        headers=admin_headers,
        json={
            "title": "Institutional Holidays Notice",
            "content": "All departments will remain closed next Monday.",
            "department_id": None
        }
    )
    assert global_ann.status_code == 201
    global_id = global_ann.json()["id"]

    # 5. Post announcement as Admin (CSE Specific)
    print("5. Posting Department CSE announcement as Admin...")
    cse_ann = client.post(
        "/api/announcements",
        headers=admin_headers,
        json={
            "title": "CSE Mini Project Guidelines",
            "content": "CSE students must submit project templates before Friday.",
            "department_id": cse_dept.id
        }
    )
    assert cse_ann.status_code == 201
    cse_id = cse_ann.json()["id"]

    # 6. Post announcement as Admin (ECE Specific)
    print("6. Posting Department ECE announcement as Admin...")
    ece_ann = client.post(
        "/api/announcements",
        headers=admin_headers,
        json={
            "title": "ECE Embedded Labs",
            "content": "Embedded Systems labs are rescheduled for Wednesday.",
            "department_id": ece_dept.id
        }
    )
    assert ece_ann.status_code == 201
    ece_id = ece_ann.json()["id"]

    # 7. Student (CSE) reads announcements (should see global + CSE, NOT ECE)
    print("7. Fetching announcements as CSE student...")
    stud_anns = client.get("/api/announcements", headers=stud_headers)
    assert stud_anns.status_code == 200
    stud_ann_ids = [ann["id"] for ann in stud_anns.json()]

    assert global_id in stud_ann_ids
    assert cse_id in stud_ann_ids
    assert ece_id not in stud_ann_ids
    print("Departmental filtering verified successfully for student role.")

    # 8. Clean up announcements
    print("8. Cleaning up announcements...")
    for aid in [global_id, cse_id, ece_id]:
        del_res = client.delete(f"/api/announcements/{aid}", headers=admin_headers)
        assert del_res.status_code == 200

    print("Cleanup verified successfully.")
    print("=== ALL ANNOUNCEMENT UPGRADE TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    try:
        test_announcements_flow()
    except Exception as e:
        print(f"Announcement tests failed: {e}")
        sys.exit(1)

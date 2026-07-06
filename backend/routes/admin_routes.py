import os
import json
from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from backend.database import get_db
from backend import models, schemas
from backend.auth import verify_admin, hash_password

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(verify_admin)])

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

@router.get("/dashboard-stats", response_model=schemas.DashboardStats)
def get_dashboard_statistics(db: Session = Depends(get_db)):
    total_students = db.query(models.Student).count()
    total_faculty = db.query(models.Faculty).count()
    total_activities = db.query(models.Activity).count()
    
    pending_activities = db.query(models.Activity).filter(models.Activity.status == "pending").count()
    approved_activities = db.query(models.Activity).filter(models.Activity.status == "approved").count()
    rejected_activities = db.query(models.Activity).filter(models.Activity.status == "rejected").count()
    
    avg_attendance = db.query(func.avg(models.Student.attendance_percentage)).scalar()
    avg_attendance = float(avg_attendance) if avg_attendance is not None else 100.0

    # Category breakdown
    category_counts = db.query(
        models.Activity.category,
        func.count(models.Activity.id)
    ).group_by(models.Activity.category).all()
    
    category_breakdown = [
        schemas.CategoryCount(category=row[0], count=row[1])
        for row in category_counts
    ]
    
    # Ensure categories are initialized if empty
    all_cats = {'internship': 0, 'project': 0, 'certification': 0, 'extracurricular': 0, 'placement': 0}
    for item in category_breakdown:
        all_cats[item.category] = item.count
    category_breakdown = [schemas.CategoryCount(category=k, count=v) for k, v in all_cats.items()]

    # Department student distribution
    dept_counts = db.query(
        models.Department.name,
        models.Department.code,
        func.count(models.Student.id)
    ).outerjoin(models.Student, models.Department.id == models.Student.department_id)\
     .group_by(models.Department.id, models.Department.name, models.Department.code).all()
     
    department_distribution = [
        schemas.DepartmentCount(department=row[0], code=row[1], student_count=row[2])
        for row in dept_counts
    ]

    return {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_activities": total_activities,
        "pending_activities": pending_activities,
        "approved_activities": approved_activities,
        "rejected_activities": rejected_activities,
        "average_attendance": avg_attendance,
        "category_breakdown": category_breakdown,
        "department_distribution": department_distribution
    }

@router.get("/users")
def list_users(role: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    users = query.all()
    
    out = []
    for u in users:
        details = {}
        if u.role == "student":
            student = db.query(models.Student).filter(models.Student.user_id == u.id).first()
            if student:
                details = {
                    "name": student.name,
                    "roll_number": student.roll_number,
                    "department": student.department.code if student.department else None,
                    "semester": student.semester
                }
        elif u.role == "faculty":
            faculty = db.query(models.Faculty).filter(models.Faculty.user_id == u.id).first()
            if faculty:
                details = {
                    "name": faculty.name,
                    "faculty_id": faculty.faculty_id,
                    "department": faculty.department.code if faculty.department else None,
                    "designation": faculty.designation
                }
        else:
            details = {"name": "Admin User"}
            
        out.append({
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at,
            "details": details
        })
    return out

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if user.role == "admin":
        # Check that we don't delete the last admin
        admin_count = db.query(models.User).filter(models.User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the final administrator account"
            )
            
    db.delete(user)
    db.commit()
    return {"message": f"User {user.email} successfully deleted"}

@router.get("/departments", response_model=List[schemas.DepartmentOut])
def get_departments(db: Session = Depends(get_db)):
    return db.query(models.Department).order_by(models.Department.name).all()

@router.post("/departments", response_model=schemas.DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(req: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Department).filter(
        (models.Department.name == req.name) | (models.Department.code == req.code)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department name or code already exists"
        )
        
    dept = models.Department(name=req.name, code=req.code)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept

@router.delete("/departments/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # We must handle or set department_id to NULL on students/faculty, which is handled by ondelete='SET NULL' in SQLAlchemy
    db.delete(dept)
    db.commit()
    return {"message": f"Department {dept.name} successfully deleted"}

@router.get("/reports/export")
def get_export_report_data(db: Session = Depends(get_db)):
    students = db.query(models.Student).order_by(models.Student.roll_number).all()
    
    report_data = []
    for s in students:
        user = db.query(models.User).filter(models.User.id == s.user_id).first()
        email = user.email if user else ""
        
        # Count approved activities
        approved_count = db.query(models.Activity).filter(
            models.Activity.student_id == s.id,
            models.Activity.status == "approved"
        ).count()
        
        report_data.append({
            "roll_number": s.roll_number,
            "name": s.name,
            "email": email,
            "department": s.department.name if s.department else "N/A",
            "department_code": s.department.code if s.department else "N/A",
            "semester": s.semester,
            "phone": s.phone or "N/A",
            "cgpa": float(s.cgpa or 0.0),
            "attendance_percentage": float(s.attendance_percentage or 100.0),
            "approved_activities_count": approved_count
        })
    return report_data

@router.post("/backup")
def backup_database(db: Session = Depends(get_db)):
    try:
        # Fetch all records from all tables
        departments = db.query(models.Department).all()
        users = db.query(models.User).all()
        students = db.query(models.Student).all()
        faculty = db.query(models.Faculty).all()
        activities = db.query(models.Activity).all()
        attendance = db.query(models.Attendance).all()
        
        backup_data = {
            "backup_timestamp": datetime.now().isoformat(),
            "departments": [
                {"id": d.id, "name": d.name, "code": d.code}
                for d in departments
            ],
            "users": [
                {"id": u.id, "email": u.email, "password_hash": u.password_hash, "role": u.role, "created_at": u.created_at.isoformat() if u.created_at else None}
                for u in users
            ],
            "students": [
                {"id": s.id, "user_id": s.user_id, "roll_number": s.roll_number, "name": s.name, "department_id": s.department_id, "semester": s.semester, "phone": s.phone, "cgpa": float(s.cgpa) if s.cgpa else 0.0, "attendance_percentage": float(s.attendance_percentage) if s.attendance_percentage else 100.0}
                for s in students
            ],
            "faculty": [
                {"id": f.id, "user_id": f.user_id, "faculty_id": f.faculty_id, "name": f.name, "department_id": f.department_id, "designation": f.designation}
                for f in faculty
            ],
            "activities": [
                {"id": a.id, "student_id": a.student_id, "title": a.title, "category": a.category, "description": a.description, "start_date": a.start_date.isoformat() if a.start_date else None, "end_date": a.end_date.isoformat() if a.end_date else None, "status": a.status, "certificate_url": a.certificate_url, "verified_by": a.verified_by, "verification_date": a.verification_date.isoformat() if a.verification_date else None, "rejection_comment": a.rejection_comment, "created_at": a.created_at.isoformat() if a.created_at else None}
                for a in activities
            ],
            "attendance": [
                {"id": att.id, "student_id": att.student_id, "date": att.date.isoformat() if att.date else None, "status": att.status, "marked_by": att.marked_by, "created_at": att.created_at.isoformat() if att.created_at else None}
                for att in attendance
            ]
        }
        
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(BACKUP_DIR, filename)
        
        with open(filepath, "w") as f:
            json.dump(backup_data, f, indent=2)
            
        return {
            "status": "success",
            "message": "Database backup completed successfully.",
            "filename": filename,
            "filepath": filepath,
            "timestamp": backup_data["backup_timestamp"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backup failed: {str(e)}"
        )

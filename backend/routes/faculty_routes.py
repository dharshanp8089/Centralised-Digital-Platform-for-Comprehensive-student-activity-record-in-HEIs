from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from backend.database import get_db
from backend import models, schemas
from backend.auth import get_current_faculty

router = APIRouter(prefix="/faculty", tags=["Faculty"])

@router.get("/students", response_model=List[schemas.StudentProfileOut])
def get_department_students(
    faculty: models.Faculty = Depends(get_current_faculty),
    db: Session = Depends(get_db)
):
    # Retrieve students in the faculty's department (if department is set)
    if not faculty.department_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faculty department not configured"
        )
        
    students = db.query(models.Student).filter(models.Student.department_id == faculty.department_id).order_by(models.Student.name).all()
    
    out = []
    for s in students:
        user = db.query(models.User).filter(models.User.id == s.user_id).first()
        email = user.email if user else ""
        out.append({
            "id": s.id,
            "roll_number": s.roll_number,
            "name": s.name,
            "email": email,
            "department_name": faculty.department.name if faculty.department else None,
            "department_code": faculty.department.code if faculty.department else None,
            "semester": s.semester,
            "phone": s.phone,
            "cgpa": float(s.cgpa or 0.0),
            "attendance_percentage": float(s.attendance_percentage or 100.0)
        })
    return out

@router.get("/pending-activities", response_model=List[schemas.ActivityOut])
def get_pending_activities(
    faculty: models.Faculty = Depends(get_current_faculty),
    db: Session = Depends(get_db)
):
    if not faculty.department_id:
        return []
        
    # Query pending activities of students belonging to the same department
    activities = db.query(models.Activity)\
        .join(models.Student, models.Activity.student_id == models.Student.id)\
        .filter(models.Student.department_id == faculty.department_id)\
        .filter(models.Activity.status == "pending")\
        .order_by(models.Activity.created_at.asc())\
        .all()
        
    out = []
    for act in activities:
        out.append({
            "id": act.id,
            "student_id": act.student_id,
            "student_name": act.student.name,
            "student_roll": act.student.roll_number,
            "title": act.title,
            "category": act.category,
            "description": act.description,
            "start_date": act.start_date,
            "end_date": act.end_date,
            "status": act.status,
            "certificate_url": act.certificate_url,
            "verified_by": act.verified_by,
            "verifier_name": None,
            "verification_date": act.verification_date,
            "rejection_comment": act.rejection_comment,
            "created_at": act.created_at
        })
    return out

@router.post("/verify-activity/{activity_id}", response_model=schemas.ActivityOut)
def verify_activity(
    activity_id: int,
    req: schemas.ActivityVerify,
    faculty: models.Faculty = Depends(get_current_faculty),
    db: Session = Depends(get_db)
):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
        
    # Ensure student belongs to the same department or the user is admin
    # (Since admin acts as a superuser, check if user is admin)
    user = db.query(models.User).filter(models.User.id == faculty.user_id).first()
    is_admin = user and user.role == "admin"
    
    if not is_admin and activity.student.department_id != faculty.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation forbidden: student belongs to a different department"
        )
        
    # Update status
    activity.status = req.status
    activity.verified_by = faculty.id
    activity.verification_date = datetime.now()
    if req.status == "rejected":
        activity.rejection_comment = req.rejection_comment
    else:
        activity.rejection_comment = None
        
    db.commit()
    db.refresh(activity)
    
    return {
        "id": activity.id,
        "student_id": activity.student_id,
        "student_name": activity.student.name,
        "student_roll": activity.student.roll_number,
        "title": activity.title,
        "category": activity.category,
        "description": activity.description,
        "start_date": activity.start_date,
        "end_date": activity.end_date,
        "status": activity.status,
        "certificate_url": activity.certificate_url,
        "verified_by": activity.verified_by,
        "verifier_name": faculty.name,
        "verification_date": activity.verification_date,
        "rejection_comment": activity.rejection_comment,
        "created_at": activity.created_at
    }

@router.post("/attendance", status_code=status.HTTP_200_OK)
def log_attendance(
    req: schemas.AttendanceBulkCreate,
    faculty: models.Faculty = Depends(get_current_faculty),
    db: Session = Depends(get_db)
):
    for record in req.records:
        # Check if student exists
        student = db.query(models.Student).filter(models.Student.id == record.student_id).first()
        if not student:
            continue
            
        # Check if attendance already exists for this date and student
        existing = db.query(models.Attendance).filter(
            models.Attendance.student_id == record.student_id,
            models.Attendance.date == req.date
        ).first()
        
        if existing:
            existing.status = record.status
            existing.marked_by = faculty.id
        else:
            new_att = models.Attendance(
                student_id=record.student_id,
                date=req.date,
                status=record.status,
                marked_by=faculty.id
            )
            db.add(new_att)
            
        db.flush() # Flush to DB so aggregation reads the latest
        
        # Recalculate student overall attendance percentage
        total_classes = db.query(func.count(models.Attendance.id)).filter(models.Attendance.student_id == record.student_id).scalar()
        present_classes = db.query(func.count(models.Attendance.id)).filter(
            models.Attendance.student_id == record.student_id,
            models.Attendance.status.in_(["present", "late"])
        ).scalar()
        
        if total_classes > 0:
            percentage = (present_classes / total_classes) * 100
        else:
            percentage = 100.0
            
        student.attendance_percentage = percentage
        
    db.commit()
    return {"message": "Attendance records successfully logged and student summary percentages updated."}

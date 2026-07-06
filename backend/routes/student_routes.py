import os
import shutil
import uuid
from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from backend.auth import get_current_student

router = APIRouter(prefix="/students", tags=["Students"])

# Save directory for uploaded certificates
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/profile", response_model=schemas.StudentProfileOut)
def get_student_profile(
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    # Query user email
    user = db.query(models.User).filter(models.User.id == student.user_id).first()
    email = user.email if user else ""
    
    # Query department details
    dept_name = student.department.name if student.department else None
    dept_code = student.department.code if student.department else None
    
    return {
        "id": student.id,
        "roll_number": student.roll_number,
        "name": student.name,
        "email": email,
        "department_name": dept_name,
        "department_code": dept_code,
        "semester": student.semester,
        "phone": student.phone,
        "cgpa": float(student.cgpa or 0.0),
        "attendance_percentage": float(student.attendance_percentage or 100.0)
    }

@router.put("/profile", response_model=schemas.StudentProfileOut)
def update_student_profile(
    req: schemas.StudentUpdate,
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    if req.phone is not None:
        student.phone = req.phone
    if req.semester is not None:
        student.semester = req.semester
    if req.cgpa is not None:
        student.cgpa = req.cgpa
    
    db.commit()
    db.refresh(student)
    
    # Fetch refreshed details
    user = db.query(models.User).filter(models.User.id == student.user_id).first()
    email = user.email if user else ""
    
    return {
        "id": student.id,
        "roll_number": student.roll_number,
        "name": student.name,
        "email": email,
        "department_name": student.department.name if student.department else None,
        "department_code": student.department.code if student.department else None,
        "semester": student.semester,
        "phone": student.phone,
        "cgpa": float(student.cgpa or 0.0),
        "attendance_percentage": float(student.attendance_percentage or 100.0)
    }

@router.get("/activities", response_model=List[schemas.ActivityOut])
def get_student_activities(
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    # Query activities for student, join with verifier if possible to return name
    activities = db.query(models.Activity).filter(models.Activity.student_id == student.id).order_by(models.Activity.created_at.desc()).all()
    
    out = []
    for act in activities:
        verifier_name = None
        if act.verifier:
            verifier_name = act.verifier.name
            
        out.append({
            "id": act.id,
            "student_id": act.student_id,
            "student_name": student.name,
            "student_roll": student.roll_number,
            "title": act.title,
            "category": act.category,
            "description": act.description,
            "start_date": act.start_date,
            "end_date": act.end_date,
            "status": act.status,
            "certificate_url": act.certificate_url,
            "verified_by": act.verified_by,
            "verifier_name": verifier_name,
            "verification_date": act.verification_date,
            "rejection_comment": act.rejection_comment,
            "created_at": act.created_at
        })
    return out

@router.post("/activities", response_model=schemas.ActivityOut)
def upload_activity(
    title: str = Form(...),
    category: str = Form(...),
    description: Optional[str] = Form(None),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    file: UploadFile = File(...),
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    # Validate category
    valid_categories = ['internship', 'project', 'certification', 'extracurricular', 'placement']
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of {valid_categories}"
        )
    
    # Save Certificate File
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save certificate document: {str(e)}"
        )
        
    certificate_url = f"/uploads/{unique_filename}"
    
    # Parse dates
    parsed_start = None
    parsed_end = None
    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            pass

    # Create Activity Record
    new_activity = models.Activity(
        student_id=student.id,
        title=title,
        category=category,
        description=description,
        start_date=parsed_start,
        end_date=parsed_end,
        status="pending",
        certificate_url=certificate_url
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    
    return {
        "id": new_activity.id,
        "student_id": new_activity.student_id,
        "student_name": student.name,
        "student_roll": student.roll_number,
        "title": new_activity.title,
        "category": new_activity.category,
        "description": new_activity.description,
        "start_date": new_activity.start_date,
        "end_date": new_activity.end_date,
        "status": new_activity.status,
        "certificate_url": new_activity.certificate_url,
        "verified_by": new_activity.verified_by,
        "verifier_name": None,
        "verification_date": new_activity.verification_date,
        "rejection_comment": new_activity.rejection_comment,
        "created_at": new_activity.created_at
    }

@router.get("/attendance", response_model=List[schemas.AttendanceOut])
def get_student_attendance(
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    attendance = db.query(models.Attendance).filter(models.Attendance.student_id == student.id).order_by(models.Attendance.date.desc()).all()
    
    out = []
    for att in attendance:
        out.append({
            "id": att.id,
            "student_id": att.student_id,
            "student_name": student.name,
            "student_roll": student.roll_number,
            "date": att.date,
            "status": att.status,
            "marked_by": att.marked_by,
            "created_at": att.created_at
        })
    return out

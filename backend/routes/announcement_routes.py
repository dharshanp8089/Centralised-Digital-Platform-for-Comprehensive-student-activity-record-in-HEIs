from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from backend.auth import get_current_user

router = APIRouter(prefix="/announcements", tags=["Announcements"])

@router.get("", response_model=List[schemas.AnnouncementOut])
def get_announcements(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch user details depending on role
    dept_id = None
    if current_user.role == "student":
        student = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
        if student:
            dept_id = student.department_id
    elif current_user.role == "faculty":
        faculty = db.query(models.Faculty).filter(models.Faculty.user_id == current_user.id).first()
        if faculty:
            dept_id = faculty.department_id

    # If admin, fetch all announcements.
    # If student or faculty, fetch global (department_id IS NULL) or department-specific announcements
    query = db.query(models.Announcement)
    if current_user.role != "admin":
        if dept_id is not None:
            query = query.filter(
                (models.Announcement.department_id == None) | 
                (models.Announcement.department_id == dept_id)
            )
        else:
            query = query.filter(models.Announcement.department_id == None)

    announcements = query.order_by(models.Announcement.created_at.desc()).all()

    # Map outputs
    out = []
    for ann in announcements:
        dept_code = ann.department.code if ann.department else None
        out.append({
            "id": ann.id,
            "title": ann.title,
            "content": ann.content,
            "created_by": ann.created_by,
            "created_at": ann.created_at,
            "department_id": ann.department_id,
            "department_code": dept_code
        })
    return out

@router.post("", response_model=schemas.AnnouncementOut, status_code=status.HTTP_201_CREATED)
def create_announcement(
    req: schemas.AnnouncementCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only faculty and admins can post announcements
    if current_user.role not in ["admin", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation forbidden: Admin or Faculty role required"
        )

    author_name = "Administrator"
    dept_id = req.department_id

    if current_user.role == "faculty":
        faculty = db.query(models.Faculty).filter(models.Faculty.user_id == current_user.id).first()
        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty profile not found"
            )
        author_name = faculty.name
        # Faculty can only post global or to their own department
        if dept_id is not None and dept_id != faculty.department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Faculty can only target announcements to their own department"
            )
    else:
        # Admin posting
        author_name = "Administrator"

    # Validate department if provided
    if dept_id is not None:
        dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target department not found"
            )

    new_ann = models.Announcement(
        title=req.title,
        content=req.content,
        created_by=author_name,
        department_id=dept_id
    )
    db.add(new_ann)
    db.commit()
    db.refresh(new_ann)

    return {
        "id": new_ann.id,
        "title": new_ann.title,
        "content": new_ann.content,
        "created_by": new_ann.created_by,
        "created_at": new_ann.created_at,
        "department_id": new_ann.department_id,
        "department_code": new_ann.department.code if new_ann.department else None
    }

@router.delete("/{announcement_id}", status_code=status.HTTP_200_OK)
def delete_announcement(
    announcement_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["admin", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation forbidden: Admin or Faculty role required"
        )

    ann = db.query(models.Announcement).filter(models.Announcement.id == announcement_id).first()
    if not ann:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    # Faculty can only delete their own announcements or announcements in their department
    if current_user.role == "faculty":
        faculty = db.query(models.Faculty).filter(models.Faculty.user_id == current_user.id).first()
        if not faculty or (ann.created_by != faculty.name and ann.department_id != faculty.department_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Faculty can only delete their own announcements"
            )

    db.delete(ann)
    db.commit()
    return {"message": "Announcement successfully deleted"}

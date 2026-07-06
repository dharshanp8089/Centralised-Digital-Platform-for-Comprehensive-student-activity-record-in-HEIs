from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from backend.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register/student", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_student(req: schemas.RegisterStudentRequest, db: Session = Depends(get_db)):
    # 1. Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == req.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2. Check if student roll number exists
    existing_roll = db.query(models.Student).filter(models.Student.roll_number == req.roll_number).first()
    if existing_roll:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Roll number already exists"
        )
        
    # 3. Check if department exists
    dept = db.query(models.Department).filter(models.Department.id == req.department_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # 4. Create User
    new_user = models.User(
        email=req.email,
        password_hash=hash_password(req.password),
        role="student"
    )
    db.add(new_user)
    db.flush() # Populate user.id

    # 5. Create Student profile
    import random
    from datetime import date, timedelta
    
    random_cgpa = round(random.uniform(7.5, 9.6), 2)
    
    new_student = models.Student(
        user_id=new_user.id,
        roll_number=req.roll_number,
        name=req.name,
        department_id=req.department_id,
        semester=req.semester,
        phone=req.phone,
        cgpa=random_cgpa,
        attendance_percentage=100.00
    )
    db.add(new_student)
    db.flush() # Populate student.id
    
    # 6. Add 5 mock attendance records for the new student
    today = date.today()
    statuses = ["present", "present", "present", "late", "absent"]
    random.shuffle(statuses)
    
    for i in range(5):
        d = today - timedelta(days=i+1)
        if d.weekday() < 5:  # weekdays only
            new_att = models.Attendance(
                student_id=new_student.id,
                date=d,
                status=statuses[i],
                marked_by=None # system marked
            )
            db.add(new_att)
            
    # Calculate exact attendance percentage based on mock logs
    total = 5
    present = sum(1 for s in statuses if s in ["present", "late"])
    new_student.attendance_percentage = round((present / total) * 100, 2)
    
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/register/faculty", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_faculty(req: schemas.RegisterFacultyRequest, db: Session = Depends(get_db)):
    # 1. Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == req.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2. Check if faculty ID exists
    existing_fac_id = db.query(models.Faculty).filter(models.Faculty.faculty_id == req.faculty_id).first()
    if existing_fac_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faculty ID already exists"
        )
        
    # 3. Check if department exists
    dept = db.query(models.Department).filter(models.Department.id == req.department_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # 4. Create User
    new_user = models.User(
        email=req.email,
        password_hash=hash_password(req.password),
        role="faculty"
    )
    db.add(new_user)
    db.flush() # Populate user.id

    # 5. Create Faculty profile
    new_faculty = models.Faculty(
        user_id=new_user.id,
        faculty_id=req.faculty_id,
        name=req.name,
        department_id=req.department_id,
        designation=req.designation
    )
    db.add(new_faculty)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.TokenResponse)
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    # 1. Find user by email
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Retrieve name based on role
    name = "Administrator"
    if user.role == "student":
        student = db.query(models.Student).filter(models.Student.user_id == user.id).first()
        if student:
            name = student.name
    elif user.role == "faculty":
        faculty = db.query(models.Faculty).filter(models.Faculty.user_id == user.id).first()
        if faculty:
            name = faculty.name
            
    # 3. Generate token
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "name": name
    }

@router.get("/departments", response_model=List[schemas.DepartmentOut])
def get_departments(db: Session = Depends(get_db)):
    return db.query(models.Department).order_by(models.Department.name).all()

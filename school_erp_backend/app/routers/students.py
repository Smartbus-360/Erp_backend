from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session,relationship

from app.database import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentResponse,StudentDetailResponse
from app.dependencies import admin_or_superadmin,employee_permission_required
from app.auth import get_current_user
from app.schemas.student_login_schema import StudentLoginCreate
from app.models.user import User
from app.security import hash_password
from app.models.student_form_config import StudentFormConfig
from app.schemas.student_form_config_schema import StudentFormConfigResponse
from fastapi import Query
from app.models.section import Section
from app.models.class_model import SchoolClass
from app.models.student_form_field import StudentFormField
from app.models.student_extra_data import StudentExtraData
from app.schemas.student_login_schema import StudentLoginUpdate
from app.security import hash_password
from app.schemas.student_login_schema import StudentPasswordUpdate
from app.models.student_form_field import StudentFormField
from app.schemas.student_form_schema import StudentFormFieldCreate



router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/", response_model=StudentResponse)

def add_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    institute_id = user.institute_id

    exists = db.query(Student).filter(
        Student.admission_no == data.admission_no,
        Student.institute_id == institute_id
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="Admission number already exists")

    # student = Student(
    #     **data.dict(),
    #     institute_id=institute_id
    # )
    # 🔹 1. Convert payload to dict
    student_data = data.dict()

# 🔹 2. REMOVE extra_fields before creating Student
    extra_fields = student_data.pop("extra_fields", None)

# 🔹 3. Create Student (ONLY core fields)
    student = Student(
    **student_data,
    institute_id=institute_id
    )

    db.add(student)
    db.commit()
    db.refresh(student)


    cls = db.query(SchoolClass).filter(
    SchoolClass.id == data.class_id,
    SchoolClass.institute_id == institute_id
    ).first()
    if not cls:
        raise HTTPException(400, "Invalid class")

# validate section
    # if data.section_id:
    #     section = db.query(Section).filter(
    #     Section.id == data.section_id,
    #     Section.class_id == data.class_id
    # ).first()
    # if not section:
    #     raise HTTPException(400, "Invalid section")
    # optional: validate section string
    if data.section and not isinstance(data.section, str):
        raise HTTPException(400, "Invalid section")


    

    # db.add(student)
    # db.commit()
    # db.refresh(student)
    if extra_fields:
        allowed_fields = db.query(StudentFormField).filter(
            StudentFormField.institute_id == institute_id,
            StudentFormField.is_active == True
        ).all()

        allowed_keys = {f.field_key for f in allowed_fields}

        for key, value in extra_fields.items():
            if key in allowed_keys:
                db.add(StudentExtraData(
                    student_id=student.id,
                    field_key=key,
                    value=str(value)
                ))

        db.commit()

    return student

# @router.get("/", response_model=list[StudentResponse])
# def list_students(
#     db: Session = Depends(get_db),
#     user=Depends(admin_or_superadmin)
# ):
#     if user.role == "superadmin":
#         return db.query(Student).all()

#     return db.query(Student).filter(
#         Student.institute_id == user.institute_id
#     ).all()

# @router.get("/", response_model=list[StudentResponse])
# def list_students(
#     db: Session = Depends(get_db),
#     user=Depends(admin_or_superadmin)
# ):
#     students = db.query(Student).filter(
#         Student.institute_id == user.institute_id
#     ).all()

#     result = []
#     for s in students:
#         user_obj = None
#         if s.user_id:
#             user_obj = db.query(User).filter(User.id == s.user_id).first()

#         result.append({
#             "id": s.id,
#             "name": s.name,
#             "admission_no": s.admission_no,
#             "class_name": s.class_name,
#             "section": s.section,
#             "has_login": bool(s.user_id),
#             "login_email": user_obj.email if user_obj else None
#         })

#     return result

@router.get("/")
def list_students(
    class_name: str | None = None,
    section: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    q = db.query(Student).filter(
        Student.institute_id == user.institute_id
    )
    
    if section:
        q = q.filter(Student.section == section)


    if class_name:
        q = q.filter(Student.class_name == class_name)

    if search:
        q = q.filter(
            Student.name.ilike(f"%{search}%") |
            Student.admission_no.ilike(f"%{search}%")
        )
    if search:
        q = q.filter(Student.name.ilike(f"%{search}%"))

    students = q.all()

    result = []
    for s in students:
        user_obj = None
        if s.user_id:
            user_obj = db.query(User).filter(User.id == s.user_id).first()

        result.append({
            "id": s.id,
            "name": s.name,
            "admission_no": s.admission_no,
            "class_name": s.class_name,
            "section": s.section,
            "has_login": bool(s.user_id),
            "login_email": user_obj.email if user_obj else None
        })

    return result

@router.get("/me", response_model=StudentResponse)
def student_profile(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.role != "student":
        raise HTTPException(status_code=403)

    student = db.query(Student).filter(
        Student.user_id == user.id
    ).first()

    if not student:
        raise HTTPException(status_code=404)

    return student

@router.post("/{student_id}/create-login")
def create_student_login(
    student_id: int,
    data: StudentLoginCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.institute_id == user.institute_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if student.user_id:
        raise HTTPException(
        status_code=400,
        detail="Login already created for this student"
        )


    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        name=student.name,
        email=data.email,
        password=hash_password(data.password),
        role="student",
        institute_id=user.institute_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    student.user_id = new_user.id
    db.commit()

    return {
        "message": "Student login created successfully",
        "email": new_user.email
    }

@router.get("/form-config", response_model=StudentFormConfigResponse)
def get_student_form_config(
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    config = db.query(StudentFormConfig).filter(
        StudentFormConfig.institute_id == user.institute_id
    ).first()

    if not config:
        config = StudentFormConfig(institute_id=user.institute_id)
        db.add(config)
        db.commit()
        db.refresh(config)

    return config

@router.get("/search")
def search_students(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    students = db.query(Student).filter(
        Student.institute_id == user.institute_id,
        Student.name.ilike(f"%{q}%")
    ).all()

    return [
        {
            "id": s.id,
            "name": s.name,
            "admission_no": s.admission_no,
            "roll_no": s.roll_no,
            "class": s.class_name,
            "class_id":s.class_id,
            "section": s.section
        }
        for s in students
    ]

@router.get("/form-fields")
def get_student_form_fields(
    db: Session = Depends(get_db),
    user = Depends(admin_or_superadmin)
):
    return db.query(StudentFormField).filter(
        StudentFormField.institute_id == user.institute_id,
        StudentFormField.is_active == True
    ).all()

@router.post("/form-fields")
def create_student_form_field(
    payload: StudentFormFieldCreate,
    db: Session = Depends(get_db),
    user = Depends(admin_or_superadmin)
):
    field = StudentFormField(
        institute_id=user.institute_id,
        field_key=payload.field_key,
        field_label=payload.field_label,
        field_type=payload.field_type,
        options=payload.options,
        is_required=payload.is_required
    )
    db.add(field)
    db.commit()
    return {"message": "Field added"}

@router.get("/{student_id}", response_model=StudentDetailResponse)
def get_student_by_id(
    student_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.institute_id == user.institute_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return student
# @router.get("/", response_model=list[StudentResponse])
# def list_students(
#     search: str | None = None,
#     class_name: str | None = None,
#     db: Session = Depends(get_db),
#     user=Depends(admin_or_superadmin)
# ):
#     q = db.query(Student).filter(
#         Student.institute_id == user.institute_id
#     )

#     if search:
#         q = q.filter(
#             Student.name.ilike(f"%{search}%") |
#             Student.admission_no.ilike(f"%{search}%")
#         )

#     if class_name:
#         q = q.filter(Student.class_name == class_name)

#     students = q.all()
#     ...

@router.post("/{student_id}/reset-login")
def reset_student_login(
    student_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.institute_id == user.institute_id
    ).first()

    if not student or not student.user_id:
        raise HTTPException(status_code=404, detail="Login not found")

    user_obj = db.query(User).filter(User.id == student.user_id).first()

    new_password = "Std@" + str(student.id)
    user_obj.password = hash_password(new_password)
    db.commit()

    return {
        "message": "Password reset successfully",
        "email": user_obj.email,
        "temp_password": new_password
    }
@router.get("/by-class/{class_id}")
def get_students_by_class_section(
    class_id: int,
    section_id: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_students"))
):
    q = db.query(Student).filter(
        Student.class_id == class_id,
        Student.institute_id == user.institute_id
    )

    if section_id:
        q = q.filter(Student.section == section_id)

    students = q.all()

    return [
        {
            "id": s.id,
            "name": s.name,
            "roll_no": s.roll_no,
            "admission_no": s.admission_no
        }
        for s in students
    ]
@router.put("/{student_id}")
def update_student(
    student_id: int,
    data: StudentCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.institute_id == user.institute_id
    ).first()

    if not student:
        raise HTTPException(404, "Student not found")

    student_data = data.dict()
    extra_fields = student_data.pop("extra_fields", None)

    for key, value in student_data.items():
        setattr(student, key, value)

    # Replace extra fields
    db.query(StudentExtraData).filter(
        StudentExtraData.student_id == student.id
    ).delete()

    if extra_fields:
        for k, v in extra_fields.items():
            db.add(StudentExtraData(
                student_id=student.id,
                field_key=k,
                value=str(v)
            ))

    db.commit()
    return {"message": "Student updated successfully"}
@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.institute_id == user.institute_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if student.user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete student with active login"
        )

    # 🔹 delete extra fields first
    db.query(StudentExtraData).filter(
        StudentExtraData.student_id == student.id
    ).delete()

    # 🔹 delete student
    db.delete(student)
    db.commit()

    return {"message": "Student deleted successfully"}
@router.put("/{student_id}/update-login")
def update_student_login(
    student_id: int,
    data: StudentLoginUpdate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.institute_id == user.institute_id
    ).first()

    if not student or not student.user_id:
        raise HTTPException(status_code=404, detail="Student login not found")

    user_obj = db.query(User).filter(User.id == student.user_id).first()

    # 🔴 prevent duplicate emails
    exists = db.query(User).filter(
        User.email == data.email,
        User.id != user_obj.id
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="Email already in use")

    user_obj.email = data.email
    db.commit()

    return {"message": "Login email updated"}
@router.put("/{student_id}/toggle-login")
def toggle_student_login(
    student_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.institute_id == user.institute_id
    ).first()

    if not student or not student.user_id:
        raise HTTPException(status_code=404, detail="Student login not found")

    user_obj = db.query(User).filter(User.id == student.user_id).first()

    user_obj.is_active = not user_obj.is_active
    db.commit()

    return {
        "message": "Login status updated",
        "is_active": user_obj.is_active
    }

@router.put("/{student_id}/change-password")
def change_student_password(
    student_id: int,
    data: StudentPasswordUpdate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.institute_id == user.institute_id
    ).first()

    if not student or not student.user_id:
        raise HTTPException(status_code=404, detail="Student login not found")

    user_obj = db.query(User).filter(User.id == student.user_id).first()
    user_obj.password = hash_password(data.password)
    db.commit()

    return {"message": "Password updated successfully"}


@router.get("/students/caste-stats")
def caste_stats(db: Session = Depends(get_db)):
    rows = db.execute("""
        SELECT caste, COUNT(*) as total
        FROM students
        WHERE caste IS NOT NULL AND caste != ''
        GROUP BY caste
        ORDER BY total DESC
    """).fetchall()

    return [
        {"label": r.caste, "count": r.total}
        for r in rows
    ]


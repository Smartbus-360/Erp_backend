from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
from app.models.class_model import SchoolClass
from app.models.promotion_log import PromotionLog
from app.dependencies import admin_or_superadmin
from app.schemas.promotion_schema import PromoteStudent
from app.models.section import Section
from app.models.student_fee import StudentFee

router = APIRouter(prefix="/promotion", tags=["Promotion"])

@router.post("/")
def promote_students(
    data: PromoteStudent,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    cls = db.query(SchoolClass).filter(
        SchoolClass.id == data.to_class_id,
        SchoolClass.institute_id == user.institute_id
    ).first()

    if not cls:
        raise HTTPException(status_code=404, detail="Target class not found")
    
    if data.to_section:
        section = db.query(Section).filter(
            Section.name == data.to_section,
            Section.class_id == data.to_class_id
    ).first()

    if not section:
        raise HTTPException(
            status_code=400,
            detail="Invalid section for target class"
        )


    students = db.query(Student).filter(
        Student.id.in_(data.student_ids),
        Student.institute_id == user.institute_id
    ).all()

    if not students:
        raise HTTPException(status_code=404, detail="No students found")


    for student in students:
        log = PromotionLog(
            student_id=student.id,
            from_class=student.class_name,
            to_class=cls.name,
            from_section=student.section,
            to_section=data.to_section,
            institute_id=user.institute_id
        )
        db.add(log)

        if (
            student.class_id == data.to_class_id and
            student.section == data.to_section
):
            continue

        student.class_id = data.to_class_id
        student.class_name = cls.name
        student.section = data.to_section

        db.query(StudentFee).filter(
            StudentFee.student_id == student.id,
            StudentFee.institute_id == user.institute_id,
            StudentFee.is_paid == False
).update({"is_paid": False})


    db.commit()
    return {"message": "Students promoted successfully"}

# @router.get("/history")
# def promotion_history(
#     db: Session = Depends(get_db),
#     user=Depends(admin_or_superadmin)
# ):
#     return db.query(PromotionLog).filter(
#         PromotionLog.institute_id == user.institute_id
#     ).order_by(PromotionLog.promoted_on.desc()).all()

# @router.get("/history")
# def promotion_history(
#     search: str | None = None,
#     from_class: str | None = None,
#     to_class: str | None = None,
#     db: Session = Depends(get_db),
#     user=Depends(admin_or_superadmin)
# ):
#     q = db.query(PromotionLog, Student).join(
#     Student, Student.id == PromotionLog.student_id
#     ).filter(
#     PromotionLog.institute_id == user.institute_id
#     )


#     if search:
#         q = q.filter(Student.name.ilike(f"%{search}%"))

#     if from_class:
#         q = q.filter(PromotionLog.from_class == from_class)

#     if to_class:
#         q = q.filter(PromotionLog.to_class == to_class)

#     # return [{
#     #     "student": p.student.name,
#     #     "from_class": p.from_class,
#     #     "from_section": p.from_section,
#     #     "to_class": p.to_class,
#     #     "to_section": p.to_section,
#     #     "date": p.promoted_on
#     # } for p in q.all()]
#     result = []

#     for log, student in q.all():
#         result.append({
#         "student": student.name,
#         "from_class": log.from_class,
#         "from_section": log.from_section,
#         "to_class": log.to_class,
#         "to_section": log.to_section,
#         "date": log.promoted_on
#         })

#     return result

@router.get("/history")
def promotion_history(
    search: str | None = None,
    from_class: str | None = None,
    to_class: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    q = db.query(PromotionLog, Student).join(
        Student, Student.id == PromotionLog.student_id
    ).filter(
        PromotionLog.institute_id == user.institute_id
    )

    if search:
        q = q.filter(Student.name.ilike(f"%{search}%"))

    if from_class:
        q = q.filter(PromotionLog.from_class == from_class)

    if to_class:
        q = q.filter(PromotionLog.to_class == to_class)

    result = []
    for log, student in q.all():
        result.append({
            "student": student.name,
            "from_class": log.from_class,
            "from_section": log.from_section,
            "to_class": log.to_class,
            "to_section": log.to_section,
            "date": log.promoted_on
        })

    return result

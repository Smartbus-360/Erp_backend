from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.exam import Exam
from app.models.exam_subject import ExamSubject
from app.models.exam_mark import ExamMark
from app.models.class_model import SchoolClass
from app.models.student import Student
from app.schemas.exam_schema import (
    ExamCreate,
    ExamResponse,
    ExamMarkCreate
)
from app.schemas.exam_schedule_schema import(
    ExamScheduleCreate,
    ExamScheduleItem
)
from app.dependencies import admin_or_superadmin, employee_permission_required
from app.models.exam_schedule import ExamSchedule
from app.models.subject import Subject
from app.auth import get_current_user

router = APIRouter(prefix="/exams", tags=["Exams"])


# @router.post("/", response_model=ExamResponse)
# def create_exam(
#     data: ExamCreate,
#     db: Session = Depends(get_db),
#     user=Depends(admin_or_superadmin)
# ):
#     cls = db.query(SchoolClass).filter(
#         SchoolClass.id == data.class_id,
#         SchoolClass.institute_id == user.institute_id
#     ).first()

#     if not cls:
#         raise HTTPException(status_code=404, detail="Class not found")

#     exam = Exam(
#         name=data.name,
#         class_id=data.class_id,
#         institute_id=user.institute_id,
#         exam_date=data.exam_date
#     )

#     db.add(exam)
#     db.commit()
#     db.refresh(exam)

#     for subject_id in data.subject_ids:
#         db.add(ExamSubject(
#             exam_id=exam.id,
#             subject_id=subject_id
#         ))

#     db.commit()
#     return exam

# @router.post("/", response_model=ExamResponse)
# def create_exam(
#     data: ExamCreate,
#     db: Session = Depends(get_db),
#     user=Depends(admin_or_superadmin)
# ):
#     if data.end_date < data.start_date:
#         raise HTTPException(400, "End date cannot be before start date")

#     exam = Exam(
#         name=data.name,
#         # class_id=data.class_id,
#         institute_id=user.institute_id,
#         start_date=data.start_date,
#         end_date=data.end_date
#     )

#     db.add(exam)
#     db.commit()
#     db.refresh(exam)

#     for subject_id in data.subject_ids:
#         db.add(ExamSubject(
#             exam_id=exam.id,
#             subject_id=subject_id
#         ))

#     db.commit()
#     return exam

@router.post("/", response_model=ExamResponse)
def create_exam(
    data: ExamCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    if data.end_date < data.start_date:
        raise HTTPException(400, "End date cannot be before start date")

    exam = Exam(
        name=data.name,
        institute_id=user.institute_id,
        start_date=data.start_date,
        end_date=data.end_date
    )

    db.add(exam)
    db.commit()
    db.refresh(exam)

    return exam


@router.get("/class/{class_id}", response_model=list[ExamResponse])
def list_exams(
    class_id: int,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_exams"))
):
    return db.query(Exam).filter(
        Exam.class_id == class_id,
        Exam.institute_id == user.institute_id
    ).all()

@router.post("/marks")
def add_exam_marks(
    data: ExamMarkCreate,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_exams"))
):
    student = db.query(Student).filter(
        Student.id == data.student_id,
        Student.institute_id == user.institute_id
    ).first()

    if not student:
        raise HTTPException(status_code=404)

    record = db.query(ExamMark).filter(
        ExamMark.exam_id == data.exam_id,
        ExamMark.student_id == data.student_id,
        ExamMark.subject_id == data.subject_id
    ).first()

    if record:
        record.marks = data.marks
    else:
        record = ExamMark(**data.dict())
        db.add(record)

    db.commit()
    return {"message": "Marks saved"}

@router.post("/{exam_id}/schedule")
def create_exam_schedule(
    exam_id: int,
    data: ExamScheduleCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    exam = db.query(Exam).filter(
        Exam.id == exam_id,
        Exam.institute_id == user.institute_id
    ).first()

    if not exam:
        raise HTTPException(404, "Exam not found")

    for item in data.schedules:
        # validate date range
        if not (exam.start_date <= item.exam_date <= exam.end_date):
            raise HTTPException(
                400,
                f"Date {item.exam_date} outside exam range"
            )

        # prevent duplicate schedule
        exists = db.query(ExamSchedule).filter(
            ExamSchedule.exam_id == exam_id,
            ExamSchedule.class_id == data.class_id,
            ExamSchedule.section_id == data.section_id,
            ExamSchedule.subject_id == item.subject_id,
            ExamSchedule.exam_date == item.exam_date,
            ExamSchedule.institute_id == user.institute_id
        ).first()

        if exists:
            raise HTTPException(
                status_code=400,
                detail="Schedule already exists"
            )

        db.add(ExamSchedule(
            exam_id=exam_id,
            class_id=data.class_id,
            section_id=data.section_id,
            subject_id=item.subject_id,
            teacher_id=item.teacher_id,
            exam_date=item.exam_date,
            institute_id=user.institute_id
        ))

    db.commit()
    return {"message": "Exam schedule added"}

@router.get("/{exam_id}/schedule")
def get_exam_schedule(
    exam_id: int,
    class_id: int,
    section_id: int,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_exams"))
):
    schedules = (
        db.query(ExamSchedule)
        .join(SchoolClass)
        .join(Subject)
        .filter(
            ExamSchedule.exam_id == exam_id,
            ExamSchedule.class_id == class_id,
            ExamSchedule.section_id == section_id,
            ExamSchedule.institute_id == user.institute_id
        )
        .order_by(ExamSchedule.exam_date)
        .all()
    )

    return [
        {
            "class_name": s.class_.name,
            "section_name": s.section.name,
            "subject_name": s.subject.name,
            "exam_date": s.exam_date.strftime("%d-%m-%Y"),
        }
        for s in schedules
    ]

@router.get("/marks")
def get_exam_marks(
    exam_id: int,
    class_id: int,
    section_id: int,
    subject_id: int,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_exams"))
):
    rows = (
        db.query(
            ExamMark.student_id,
            Student.name.label("student_name"),
            ExamMark.marks
        )
        .join(Student, Student.id == ExamMark.student_id)
        .filter(
            ExamMark.exam_id == exam_id,
            ExamMark.subject_id == subject_id,
            Student.class_id == class_id,
            Student.section_id == section_id,
            Student.institute_id == user.institute_id
        )
        .order_by(Student.roll_no)
        .all()
    )

    return [
        {
            "student_id": r.student_id,
            "student_name": r.student_name,
            "marks": r.marks
        }
        for r in rows
    ]
@router.get("/{exam_id}")
def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_exams"))
):
    exam = db.query(Exam).filter(
        Exam.id == exam_id,
        Exam.institute_id == user.institute_id
    ).first()

    if not exam:
        raise HTTPException(status_code=404, detail="Not Found")

    # subjects = (
    #     db.query(ExamSubject.subject_id)
    #     .filter(ExamSubject.exam_id == exam.id)
    #     .all()
    # )
    subjects = (
    db.query(Subject.id, Subject.name)
    .join(ExamSubject, ExamSubject.subject_id == Subject.id)
    .filter(ExamSubject.exam_id == exam.id)
    .all()
    )


    return {
        "id": exam.id,
        "name": exam.name,
        # "class_id": exam.class_id,
        "start_date": exam.start_date,
        "end_date": exam.end_date,
        # "subjects": [
        #     {"id": s.subject_id} for s in subjects
        # ]
        "subjects": [
        {"id": s.id, "name": s.name} for s in subjects
    ]

    }
@router.get("/", response_model=list[ExamResponse])
def get_all_exams(
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_exams"))
):
    # return db.query(Exam).filter(
    #     Exam.institute_id == user.institute_id
    # ).all()
    exams = db.query(Exam).filter(
    Exam.institute_id == user.institute_id
    ).all()

    return [
        {
        "id": e.id,
        "name": e.name,
        "start_date": e.start_date,
        "end_date": e.end_date
        }
        for e in exams
    ]


@router.get("/{exam_id}/result")
def get_exam_result(
    exam_id: int,
    class_id: int,
    section_id: int,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_exams"))
):
    rows = (
        db.query(
            Student.id,
            Student.name,
            Subject.name.label("subject"),
            ExamMark.marks
        )
        .join(ExamMark, ExamMark.student_id == Student.id)
        .join(Subject, Subject.id == ExamMark.subject_id)
        .filter(
            ExamMark.exam_id == exam_id,
            Student.class_id == class_id,
            Student.section_id == section_id,
            Student.institute_id == user.institute_id
        )
        .order_by(Student.roll_no)
        .all()
    )

    result = {}
    for r in rows:
        result.setdefault(r.id, {
            "student_name": r.name,
            "marks": {}
        })["marks"][r.subject] = r.marks

    return result

@router.get("/student/my-exams")
def get_student_exams(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "student":
        raise HTTPException(status_code=403)

    student = db.query(Student).filter(
        Student.user_id == user.id,
        Student.institute_id == user.institute_id
    ).first()

    if not student:
        raise HTTPException(404, "Student not found")

    exams = (
        db.query(Exam)
        .filter(
            Exam.institute_id == user.institute_id,
        )
        .order_by(Exam.start_date)
        .all()
    )

    return exams
@router.get("/student/exams/{exam_id}/schedule")
def get_student_exam_schedule(
    exam_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "student":
        raise HTTPException(status_code=403)

    student = db.query(Student).filter(
        Student.user_id == user.id,
        Student.institute_id == user.institute_id
    ).first()

    if not student:
        raise HTTPException(404)

    schedules = (
        db.query(ExamSchedule)
        .join(Subject)
        .filter(
            ExamSchedule.exam_id == exam_id,
            ExamSchedule.class_id == student.class_id,
            ExamSchedule.section_id == student.section_id,
            ExamSchedule.institute_id == user.institute_id
        )
        .order_by(ExamSchedule.exam_date)
        .all()
    )

    return [
        {
            "subject": s.subject.name,
            "date": s.exam_date.strftime("%d-%m-%Y")
        }
        for s in schedules
    ]
@router.get("/student/exams/{exam_id}/result")
def get_student_exam_result(
    exam_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "student":
        raise HTTPException(status_code=403)

    student = db.query(Student).filter(
        Student.user_id == user.id,
        Student.institute_id == user.institute_id
    ).first()

    if not student:
        raise HTTPException(404)

    rows = (
        db.query(
            Subject.name.label("subject"),
            ExamMark.marks
        )
        .join(Subject, Subject.id == ExamMark.subject_id)
        .filter(
            ExamMark.exam_id == exam_id,
            ExamMark.student_id == student.id
        )
        .all()
    )

    return {
        "exam_id": exam_id,
        "student": student.name,
        "marks": {r.subject: r.marks for r in rows}
    }


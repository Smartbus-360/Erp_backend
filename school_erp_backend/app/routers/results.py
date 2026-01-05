from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.exam import Exam
from app.models.exam_mark import ExamMark
from app.models.subject import Subject
from app.models.student import Student
from app.dependencies import employee_permission_required
from app.auth import get_current_user
from app.schemas.result_schema import ResultCard, SubjectResult

router = APIRouter(prefix="/results", tags=["Results"])

@router.get("/student/{student_id}/exam/{exam_id}", response_model=ResultCard)
def get_result_card(
    student_id: int,
    exam_id: int,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_exams"))
):
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.institute_id == user.institute_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    exam = db.query(Exam).filter(
        Exam.id == exam_id,
        Exam.institute_id == user.institute_id
    ).first()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    marks = db.query(
        ExamMark.marks,
        Subject.name.label("subject_name")
    ).join(
        Subject, Subject.id == ExamMark.subject_id
    ).filter(
        ExamMark.exam_id == exam_id,
        ExamMark.student_id == student_id
    ).all()

    if not marks:
        raise HTTPException(status_code=404, detail="No marks found")

    subject_results = []
    total = 0
    failed = False

    for m in marks:
        subject_results.append(
            SubjectResult(
                subject_name=m.subject_name,
                marks=m.marks
            )
        )
        total += m.marks
        if m.marks < 33:
            failed = True

    percentage = round(total / (len(marks) * 100) * 100, 2)

    return ResultCard(
        student_id=student.id,
        student_name=student.name,
        class_name=student.class_name,
        exam_name=exam.name,
        subjects=subject_results,
        total_marks=total,
        percentage=percentage,
        result="FAIL" if failed else "PASS"
    )

@router.get("/me/exam/{exam_id}", response_model=ResultCard)
def student_my_result(
    exam_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "student":
        raise HTTPException(status_code=403)

    student = db.query(Student).filter(
        Student.user_id == user.id
    ).first()

    if not student:
        raise HTTPException(status_code=404)

    return get_result_card(
        student_id=student.id,
        exam_id=exam_id,
        db=db,
        user=user
    )


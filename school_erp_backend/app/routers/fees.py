from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models.student_fee import StudentFee
from app.models.student import Student
from app.dependencies import employee_permission_required
from app.models.fee_structure import FeeStructure
from app.models.fee_payment import FeePayment
from app.schemas.fees_schema import (
    FeeStructureCreate,
    GenerateFee,
    CollectFee,
    SaveFeeStructureRequest
)
from app.dependencies import admin_or_superadmin
from app.models.fee_fine_rule import FeeFineRule
from app.models.fee_structure import FeeStructure
from app.dependencies import admin_or_superadmin
from app.utils.fee_fine_calculator import calculate_fine


router = APIRouter(prefix="/fees", tags=["Fees"])


@router.post("/structure")
def create_fee_structure(
    data: FeeStructureCreate,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_fees"))
):
    fs = FeeStructure(
        **data.dict(),
        institute_id=user.institute_id
    )
    # Validate at least one scope
    if not (data.class_id or data.student_id):
        pass  # institute-wide fee allowed

# Prevent conflicting definitions
    if data.student_id and (data.class_id or data.section_id):
        raise HTTPException(
        400,
        "Student-specific fee cannot have class or section"
    )
    if data.scope == "ALL":
        data.class_id = None
        data.section_id = None
        data.student_id = None

    elif data.scope == "CLASS":
        if not data.class_id:
            raise HTTPException(400, "class_id required for CLASS fee")
        data.student_id = None

    elif data.scope == "STUDENT":
        if not data.student_id:
            raise HTTPException(400, "student_id required for STUDENT fee")
        data.class_id = None
        data.section_id = None


    db.add(fs)
    db.commit()
    return {"message": "Fee structure created"}

@router.post("/generate")
def generate_student_fee(
    data: GenerateFee,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_fees"))
):
    student = db.query(Student).filter(
        Student.id == data.student_id,
        Student.institute_id == user.institute_id
    ).first()

    if not student:
        raise HTTPException(status_code=404)

    structures = db.query(FeeStructure).filter(
        # FeeStructure.class_id == data.class_id,
        FeeStructure.institute_id == user.institute_id,
        (
        (FeeStructure.student_id == data.student_id) |
        (
            (FeeStructure.class_id == data.class_id) &
            (FeeStructure.section_id == student.section_id) &
            (FeeStructure.student_id == None)
        ) |
        (
            (FeeStructure.class_id == data.class_id) &
            (FeeStructure.section_id == None) &
            (FeeStructure.student_id == None)
        ) |
        (
            (FeeStructure.class_id == None) &
            (FeeStructure.student_id == None)
        )

    )
    ).all()

    total = sum(f.amount for f in structures)

    sf = StudentFee(
        student_id=data.student_id,
        class_id=data.class_id,
        total_amount=total,
        institute_id=user.institute_id
    )

    db.add(sf)
    db.commit()
    db.refresh(sf)
    return {"total_amount": total,"student_fee_id":sf.id}

@router.post("/collect")
def collect_fee(
    data: CollectFee,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_fees"))
):
    sf = db.query(StudentFee).filter(
        StudentFee.id == data.student_fee_id,
        StudentFee.institute_id == user.institute_id
    ).first()

    if not sf:
        raise HTTPException(status_code=404)
    
    rule = db.query(FeeFineRule).filter(
        FeeFineRule.institute_id == user.institute_id
    ).first()

    # 🔹 2. Calculate fine (AUTO)
    fine_amount = calculate_fine(
        due_date=sf.due_date or sf.created_date,
        rule=rule
    )


    # 🔹 3. Total payable
    total_payable = sf.total_amount + fine_amount

    # sf.paid_amount += data.amount
    # if sf.paid_amount >= sf.total_amount:
    #     sf.is_paid = True
    #     sf.fine_amount = fine_amount

    sf.paid_amount += data.amount

    total_payable = sf.total_amount + fine_amount

# lock fine only once
    if sf.fine_amount == 0:
        sf.fine_amount = fine_amount

    if sf.paid_amount >= total_payable:
        sf.is_paid = True


    payment = FeePayment(
        **data.dict(),
        institute_id=user.institute_id
    )

    db.add(payment)
    db.commit()
    return {
        "message": "Fee collected",
        "fine_applied": fine_amount,
        "total_payable": total_payable,
        "paid": sf.paid_amount,
        "due": max(total_payable - sf.paid_amount, 0)
    }

@router.get("/defaulters")
def fee_defaulters(
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_fees"))
):
    # return db.query(StudentFee).filter(
    #     StudentFee.is_paid == False,
    #     StudentFee.institute_id == user.institute_id
    # ).all()
    defaulters = db.query(StudentFee).filter(
    StudentFee.is_paid == False,
    StudentFee.institute_id == user.institute_id
    ).all()

    result = []

    for sf in defaulters:
        student = db.query(Student).filter(Student.id == sf.student_id).first()

        total_payable = sf.total_amount + sf.fine_amount
        due_amount = total_payable - sf.paid_amount

        result.append({
        "name": student.name,
        "class": student.class_name,
        "section": student.section,
        "due_amount": due_amount
        })

    return result

@router.get("/invoice/{student_fee_id}")
def fee_invoice_preview(
    student_fee_id: int,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_fees"))
):
    sf = db.query(StudentFee).filter(
        StudentFee.id == student_fee_id,
        StudentFee.institute_id == user.institute_id
    ).first()

    if not sf:
        raise HTTPException(status_code=404)

    student = db.query(Student).filter(Student.id == sf.student_id).first()

    structures = db.query(FeeStructure).filter(
        FeeStructure.class_id == sf.class_id,
        FeeStructure.institute_id == user.institute_id
    ).all()

    # fine = 0
    # rule = db.query(FeeFineRule).filter(
    # FeeFineRule.institute_id == user.institute_id
    #     ).first()

    # if rule:
    #     days_late = max((date.today() - sf.createdAt).days - rule.grace_days, 0)

    #     if rule.fine_type == "daily":
    #         fine = days_late * rule.fine_amount

    total_payable = sf.total_amount + sf.fine_amount

    return {
        "student": {
            "id": student.id,
            "name": student.name,
            "admission_no": student.admission_no, # ✅ exists
            "roll_no": student.roll_no,            # ✅ exists
            "class": student.class_name,           # ✅ exists
            "section": student.section
        },
        "fees": [
            {"name": f.fee_name, "amount": f.amount}
            for f in structures
        ],
        # "total": sf.total_amount,
        # "paid": sf.paid_amount,
        # "due": sf.total_amount - sf.paid_amount

        "total": total_payable,
        "base_amount": sf.total_amount,
        "fine": sf.fine_amount,
        "paid": sf.paid_amount,
        "due": total_payable - sf.paid_amount

    }
@router.get("/payments")
def fee_payments(
    student_id: int,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_fees"))
):
    payments = db.query(FeePayment).filter(
        FeePayment.student_fee_id.in_(
            db.query(StudentFee.id).filter(
                StudentFee.student_id == student_id,
                StudentFee.institute_id == user.institute_id
            )
        )
    ).all()

    return payments

@router.get("/receipt/{student_fee_id}")
def fee_paid_receipt(
    student_fee_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    sf = db.query(StudentFee).filter(
        StudentFee.id == student_fee_id,
        StudentFee.institute_id == user.institute_id
    ).first()

    if not sf:
        raise HTTPException(status_code=404)

    student = db.query(Student).filter(Student.id == sf.student_id).first()

    payments = db.query(FeePayment).filter(
        FeePayment.student_fee_id == student_fee_id
    ).all()

    total_paid = sum(p.amount for p in payments)

    return {
        "student": {
            "name": student.name,
            "admission_no": student.admission_no,
            "class": student.class_name,
            "section": student.section
        },
        "total_amount": sf.total_amount,
        "paid_amount": total_paid,
        "due_amount": sf.total_amount - total_paid,
        "payments": [
            {
                "amount": p.amount,
                "mode": p.payment_mode,
                "date": p.payment_date
            }
            for p in payments
        ]
    }

@router.get("/history")
def fee_history(
    student_id: int,
    month: str,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    sf = db.query(StudentFee).filter(
        StudentFee.student_id == student_id,
        StudentFee.institute_id == user.institute_id
    ).first()

    if not sf:
        return []

    payments = db.query(FeePayment).filter(
        FeePayment.student_fee_id == sf.id,
        FeePayment.payment_date.like(f"{month}%")
    ).all()

    return {
        "student": {
            "name": sf.student.name,
            "admission_no": sf.student.admission_no,
            "class": sf.student.class_name,
            "section": sf.student.section
        },
        "total_amount": sf.total_amount,
        "paid_amount": sum(p.amount for p in payments),
        "payments": [
            {
                "amount": p.amount,
                "mode": p.payment_mode,
                "date": p.payment_date
            }
            for p in payments
        ]
    }

@router.get("/structure")
def list_fee_structures(
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    return db.query(FeeStructure).filter(
        FeeStructure.institute_id == user.institute_id
    ).all()

# @router.get("/structure/by-scope")
# def get_fee_by_scope(
#     scope: str,
#     class_id: int | None = None,
#     student_id: int | None = None,
#     db: Session = Depends(get_db),
#     user=Depends(admin_or_superadmin)
# ):
#     q = db.query(FeeStructure).filter(
#         FeeStructure.institute_id == user.institute_id,
#         FeeStructure.scope == scope
#     )

#     if scope == "CLASS":
#         q = q.filter(FeeStructure.class_id == class_id)
#         FeeStructure.scope.in_(["CLASS", "ALL"])

#     if scope == "STUDENT":
#         q = q.filter(FeeStructure.student_id == student_id)

#     return q.all()

@router.get("/structure/by-scope")
def get_fee_by_scope(
    scope: str,
    class_id: int | None = None,
    section_id: int | None = None,
    student_id: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    q = db.query(FeeStructure).filter(
        FeeStructure.institute_id == user.institute_id
    )

    if scope == "ALL":
        q = q.filter(FeeStructure.scope == "ALL")

    elif scope == "CLASS":
        q = q.filter(
            FeeStructure.scope == "CLASS",
            FeeStructure.class_id == class_id
        )
        if section_id:
            q = q.filter(FeeStructure.section_id == section_id)

    elif scope == "STUDENT":
        q = q.filter(
            FeeStructure.scope == "STUDENT",
            FeeStructure.student_id == student_id
        )

    return q.all()


@router.post("/structure/save", dependencies=[Depends(admin_or_superadmin)])
def save_fee_structure(payload: SaveFeeStructureRequest, db: Session = Depends(get_db),user = Depends(admin_or_superadmin)):

    # Remove old entries for same scope
    # q = db.query(FeeStructure).filter(FeeStructure.scope == payload.scope)
    q = db.query(FeeStructure).filter(
    FeeStructure.scope == payload.scope,
    FeeStructure.institute_id == user.institute_id
)

    if payload.scope == "CLASS":
        q = q.filter(
            FeeStructure.class_id == payload.class_id,
            FeeStructure.section_id == payload.section_id
        )

    if payload.scope == "STUDENT":
        q = q.filter(FeeStructure.student_id == payload.student_id)

    q.delete(synchronize_session=False)

    # Insert fresh data
    for item in payload.fees:
        db.add(FeeStructure(
            scope=payload.scope,
            class_id=payload.class_id,
            section_id=payload.section_id,
            student_id=payload.student_id,
            fee_name=item.fee_name,
            amount=item.amount,
                    institute_id=user.institute_id   # ✅ REQUIRED

        ))

    db.commit()
    return {"status": "success", "message": "Fee structure saved"}

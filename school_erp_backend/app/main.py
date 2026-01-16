from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth,institute,students,attendance,employees,attendance_reports,classes,subjects,exams,results,fees,homework,salary,promotion,dashboard,reports,students_search,sections,syllabus,fee_fine,timetable,weekday,period,messages,notifications,dashboard1,employee_roles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="School ERP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
                "https://erp.webadmin.smartbus360.com",
                "https://erp.backend.smartbus360.com",
        "http://127.0.0.1:8001",
        "http://localhost:8001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(institute.router)
app.include_router(students.router)
app.include_router(attendance.router)
app.include_router(employees.router)
app.include_router(attendance_reports.router)
app.include_router(classes.router)
app.include_router(subjects.router)
app.include_router(exams.router)
app.include_router(results.router)
app.include_router(fees.router)
app.include_router(homework.router)
app.include_router(salary.router)
app.include_router(promotion.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(students_search.router)
app.include_router(sections.router)
app.include_router(syllabus.router)
app.include_router(fee_fine.router)
app.include_router(timetable.router)
app.include_router(weekday.router)
app.include_router(period.router)
app.include_router(messages.router)
app.include_router(notifications.router)
app.include_router(dashboard1.router)
app.include_router(employee_roles.router)


@app.get("/")
def root():
    return {"status": "ERP Backend Running"}

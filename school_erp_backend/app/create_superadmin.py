from app.database import SessionLocal
from app.models.user import User
from app.security import hash_password

db = SessionLocal()

user = User(
    name="Super Admin",
    email="superadmin@erp.com",
    password=hash_password("admin123"),
    role="superadmin",
    institute_id=None
)

db.add(user)
db.commit()
db.close()

print("SuperAdmin created")

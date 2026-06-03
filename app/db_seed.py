"""Seed roles and default admin user. Run once or on first deploy."""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Role, UserRole
from app.core.security import hash_password


def seed(db: Session) -> None:
    if db.query(Role).count() > 0:
        return
    for code, name in [("ADMIN", "Administrator"), ("FLEET_MANAGER", "Fleet Manager"), ("DRIVER", "Driver")]:
        db.add(Role(code=code, name=name))
    db.commit()
    admin_role = db.query(Role).filter(Role.code == "ADMIN").first()
    if not admin_role:
        return
    if db.query(User).filter(User.email == "admin@logistics.local").first():
        return
    admin = User(
        email="admin@logistics.local",
        password_hash=hash_password("admin123"),
        full_name="System Admin",
        is_active=True,
    )
    db.add(admin)
    db.flush()
    db.add(UserRole(user_id=admin.id, role_id=admin_role.id, scope_zone_id=None))
    db.commit()


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
        print("Seed done: roles + admin@logistics.local / admin123")
    finally:
        db.close()

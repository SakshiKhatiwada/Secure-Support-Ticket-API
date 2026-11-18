from fastapi import HTTPException
from sqlmodel import Session

from app.data import Role
from app.models.user import UserDB
from app.utils.passwords import hash_password
from app.config import settings
from app.dependencies.session import engine

def create_initial_admin(session: Session):
    
    admin = UserDB(
        username="adminsakshi",
        hashed_password=hash_password(settings.initial_admin_password),
        role=Role.ADMIN
    )
    try:
        session.add(admin)
        session.commit()
    except:
        session.rollback()
        raise HTTPException(status_code=500, detail="something went wrong")
    
    print("Admin created successfully")
    
if __name__ == "__main__":
    with Session(engine) as session:
        create_initial_admin(session)
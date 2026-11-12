from sqlmodel import select

from app.dependencies.session import SessionDep
from app.models.user import UserDB


def if_already_exists(username: str, session: SessionDep) -> bool:
    user = session.exec(
        select(UserDB).where(UserDB.username == username)
    ).first()
    
    if user:
        return True
    return False
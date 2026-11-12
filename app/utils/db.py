from sqlmodel import select

from app.dependencies.session import SessionDep
from app.models.ticket import TicketDB
from app.models.user import UserDB


def if_already_exists(username: str, session: SessionDep) -> bool:
    user = session.exec(
        select(UserDB).where(UserDB.username == username)
    ).first()
    
    if user:
        return True
    return False

def get_user_from_db(username: str, session: SessionDep):
    return session.exec(
            select(UserDB).where(UserDB.username == username)
        ).first()
    
def get_tickets_from_db(session: SessionDep, user_id: int | None = None):
    
    statement = select(TicketDB)
    
    if user_id is not None:
        statement = statement.where(
            TicketDB.owner_id == user_id
        )
    
    results = session.exec(statement).all()
    
    return results
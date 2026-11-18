from fastapi import HTTPException, status
from sqlmodel import select

from app.data import Role
from app.dependencies.session import SessionDep
from app.models.ticket import TicketDB, TicketStatusUpdate
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
    
def get_all_users_from_db(session: SessionDep):
    return session.exec(
        select(UserDB)
    ).all()
    
def get_tickets_from_db(session: SessionDep, user_id: int | None = None):
    
    statement = select(TicketDB)
    
    if user_id is not None:
        statement = statement.where(
            TicketDB.owner_id == user_id
        )
    
    results = session.exec(statement).all()
    
    return results

def get_individual_ticket_from_db(session: SessionDep, tid: int, current_user: UserDB):
    # ticket = session.get(TicketDB, tid)
    # if current_user.role in (Role.STAFF, Role.ADMIN):
    #     return ticket
    
    # Another Approach
    statement = select(TicketDB).where(TicketDB.id == tid)
    
    if current_user.role not in (Role.STAFF, Role.ADMIN):
        statement = statement.where(
            TicketDB.owner_id == current_user.id
        )
        
    ticket = session.exec(statement).first()
    
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid ticket id") # this way, it avoid exposing whether another user's ticket exists, imp for privacy and preventing resource enumeration
    
    
    # Regular user can access only their own tickets
    # if ticket.owner_id != current_user.id: # is not would have checked oject identity (reference point)
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to access this ticket")
    return ticket
    
def update_ticket_status_in_db(current_user: UserDB, tid: int, ticket_status_info: TicketStatusUpdate,session: SessionDep):
    if current_user.role == Role.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied"
        )
        
    db_ticket = session.get(TicketDB, tid) # tid is PK
    
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ticket not found"
        )
    
    ticket_data = ticket_status_info.model_dump(exclude_unset=True)
    
    db_ticket.sqlmodel_update(ticket_data)
    
    session.add(db_ticket)
    session.commit()
    session.refresh(db_ticket)
    return db_ticket
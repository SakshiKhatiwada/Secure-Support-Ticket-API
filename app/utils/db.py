from fastapi import HTTPException, status
from sqlmodel import select

from app.data import Role, TicketStatus
from app.dependencies.session import SessionDep
from app.models.ticket import TicketDB, TicketStatusUpdate, UpdateTicket
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
    
def get_tickets_from_db(session: SessionDep, user_id: int | None = None, ticket_status: TicketStatus | None = None):
    
    statement = select(TicketDB)
    
    if user_id is not None:
        statement = statement.where(
            TicketDB.owner_id == user_id
        )
        
    if ticket_status:
        statement = statement.where(TicketDB.status == ticket_status)
    
    results = session.exec(statement).all()
    
    # return results.sort(key=lambda ticket: ticket.id) # IMP .sort() returns None as it modifies the original list
    
    results.sort(key=lambda ticket: ticket.id)
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
    
def update_ticket_status_in_db(tid: int, ticket_status_info: TicketStatusUpdate,session: SessionDep):
    # if current_user.role == Role.USER:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="permission denied"
    #     )
        
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

def delete_ticket_from_db(tid: int, session: SessionDep):
    ticket = session.get(TicketDB, tid) 
    try:
        session.delete(ticket)
        session.commit()
    except:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="something went wrong")
    return

def update_ticket(tid: int, ticket_info: UpdateTicket, current_user: UserDB, session: SessionDep):
    db_ticket = session.get(TicketDB, tid)
    
    if db_ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    
    if current_user.id != db_ticket.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission Denied")
        
    if db_ticket.status is not TicketStatus.OPEN:    
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ticket already under approval")
    
    db_ticket.sqlmodel_update(ticket_info.model_dump())

    try: 
        session.add(db_ticket)
        session.commit()
        session.refresh(db_ticket)
        
    except: 
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error occurred"
        )
        
    return db_ticket
        

    
from sqlite3 import IntegrityError
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from app.data import Role
from app.dependencies.role_checker import StaffOrAdmin
from app.dependencies.session import SessionDep
from app.dependencies.user import get_current_user
from app.models.ticket import TicketDB, TicketPublic, CreateTicket
from app.models.user import UserDB
from app.utils.db import get_tickets_from_db

UserDep = Annotated[UserDB, Depends(get_current_user)]

router = APIRouter(prefix="/tickets", tags=['Tickets'])

@router.post("", response_model=TicketPublic)
def create_ticket(ticket: CreateTicket, current_user : UserDep, session: SessionDep):
    new_ticket = TicketDB(
        **ticket.model_dump(),
        owner_id=current_user.id,
        status="open"
    )
    
    try:
        session.add(new_ticket)
        session.commit()
        session.refresh(new_ticket)
    except:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error Occurred. Terminated")
    
    return new_ticket

@router.get("", status_code=200)
def get_tickets(current_user : UserDep, session: SessionDep):
    
    if current_user.role in [Role.STAFF, Role.ADMIN]:
        tickets = get_tickets_from_db(session)
    else:
        tickets = get_tickets_from_db(session, user_id=current_user.id)
    
    return tickets
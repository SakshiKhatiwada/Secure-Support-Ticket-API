from sqlite3 import IntegrityError
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from app.data import Role
from app.dependencies.role_checker import StaffOrAdmin
from app.dependencies.session import SessionDep
from app.dependencies.user import get_current_user
from app.models.ticket import TicketDB, TicketPublic, CreateTicket, TicketStatusUpdate, UpdateTicket
from app.models.user import UserDB
from app.utils.db import delete_ticket_from_db, get_individual_ticket_from_db, get_tickets_from_db, update_ticket, update_ticket_status_in_db

UserDep = Annotated[UserDB, Depends(get_current_user)]

router = APIRouter(prefix="/tickets", tags=['Tickets'])

@router.post("", response_model=TicketPublic, status_code=201)
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

@router.get("/{tid}", status_code=200)
def get_individual_ticket(tid: int, current_user: UserDep, session: SessionDep):
    return get_individual_ticket_from_db(session, tid, current_user)

@router.put("/{tid}", status_code=200)
def put_ticket(tid: int, ticket_info: UpdateTicket, current_user: UserDep, session: SessionDep):
    return update_ticket(tid, ticket_info, current_user, session)

@router.patch("/{tid}/status", status_code=200)
def update_ticket_status(tid: int, status_info: TicketStatusUpdate, current_user: UserDep, session: SessionDep):
    return update_ticket_status_in_db(current_user=current_user, ticket_status_info=status_info, tid=tid, session=session)

@router.delete("/{tid}", status_code=204)
def delete_ticket(tid: int, current_user: UserDep, session: SessionDep):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="permission denied")
    delete_ticket_from_db(tid, session)
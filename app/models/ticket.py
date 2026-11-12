from typing import Literal

from sqlmodel import SQLModel, Field
from pydantic import ConfigDict

from app.data import TicketStatus

class CreateTicket(SQLModel):
    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=5, max_length=2000)
    
    model_config = ConfigDict(extra="forbid")
    
class TicketStatusUpdate(SQLModel):
    status: TicketStatus
    
class TicketDB(CreateTicket, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="userdb.id", ondelete="RESTRICT")
    status: TicketStatus # Literal doesn't work here, not for sqlmodel table
    
class TicketPublic(TicketDB):
    pass
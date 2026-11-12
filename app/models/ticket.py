from typing import Literal

from sqlmodel import SQLModel, Field
from pydantic import ConfigDict

class CreateTicket(SQLModel):
    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=5, max_length=2000)
    
    model_config = ConfigDict(extra="forbid")
    
class TicketStatus(SQLModel):
    status: Literal["open", "in_progress", "resolved"]
    
class TicketDB(CreateTicket, Table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="userdb.id", ondelete="RESTRICT")
    status: Literal["open", "in_progress", "resolved"]
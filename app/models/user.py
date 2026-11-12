from sqlmodel import SQLModel, Field
from typing import Literal
from pydantic import ConfigDict

class Register(SQLModel):
    username: str = Field(unique=True, index=True, min_length=3, max_length=30, regex=r"^[a-z0-9_]+$")
    password: str = Field(min_length=15, max_length=128)
    
    model_config = ConfigDict(extra="forbid")
    
class UserDB(SQLModel, Table=True):
    id: int
    username: str = Field(unique=True, index=True, min_length=3, max_length=30)
    hashed_password: str
    role: Literal["user", "staff", "admin"] = "user"
    is_active: bool = True
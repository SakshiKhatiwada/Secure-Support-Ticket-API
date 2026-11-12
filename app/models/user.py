from sqlmodel import SQLModel, Field
from pydantic import ConfigDict

from app.data import Role

class Register(SQLModel):
    username: str = Field(unique=True, index=True, min_length=3, max_length=30, regex=r"^[a-z0-9_]+$")
    password: str = Field(min_length=15, max_length=128)
    
    model_config = ConfigDict(extra="forbid")
    
class UserDB(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=30)
    hashed_password: str
    role: Role = Field(default=Role.USER)
    # role: Literal["user", "staff", "admin"] = "user"
    is_active: bool = True
    
class UserPublic(SQLModel):
    username: str = Field(unique=True)
    role: Role

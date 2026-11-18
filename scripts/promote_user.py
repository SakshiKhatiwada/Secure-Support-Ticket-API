import sys #built-in Python module that provides access to variables and functionality related to the Python interpreter and its execution environment.

from sqlmodel import Session, select

from app.data import Role
from app.dependencies.session import engine
from app.models.user import UserDB

def promote_user(username: str, new_role: Role):
    with Session(engine) as session:
        
        statement = select(UserDB).where(
            UserDB.username == username
        )
        
        user = session.exec(statement).first()
        
        if not user:
            print("user not found")
            return
        
        user.role = new_role
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        print(
            f"Successfully promoted {username} to {new_role.value}"
        )
        
if __name__ == "__main__":
    
    # check if complete parameters are given
    if len(sys.argv)<3: # terminal kaa args haru
        print(
            "Usage: python scripts/promote_user.py"
            "<username> <role>"
        )
        
        sys.exit(1) # terminated with error
        
    # normalize username and role
    username = sys.argv[1].strip().lower()
    requested_role = sys.argv[2].lower()
    
    # check if role exists in Role enum
    try:
        new_role = Role(requested_role)
    except ValueError:
        print("Invalid Role. Allowed: user, staff, admin")
        sys.exit(1)
        
    confirm = "--confirm" in sys.argv
    
    if requested_role == "admin" and not confirm:
        print("Admin promotion requires --confirm.")
        sys.exit(1)
        
    # call the function
    promote_user(username, new_role)
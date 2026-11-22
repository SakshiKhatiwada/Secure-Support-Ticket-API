# this file creates a temporary db, tables, sessions and test client

from fastapi import HTTPException, status

from fastapi.testclient import TestClient
import pytest
from sqlmodel import SQLModel, Session, create_engine

from app.data import Role
from app.models.user import UserDB # registering purpose ko laagi ho, explicitly katai use nabhaye pani
from app.models.ticket import TicketDB

from app.main import app
from app.dependencies.session import get_session
from app.utils.auth import create_token

from app.utils.passwords import hash_password
from app.utils.tokens import set_token_expiry

@pytest.fixture
def engine(tmp_path): # tmp_path= built-in python fixture; provides unique, temporary directory for each test invocation
    
    db_path = tmp_path/"test_database.db"
    
    test_engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    
    SQLModel.metadata.create_all(test_engine)
    
    yield test_engine
    
    SQLModel.metadata.drop_all(test_engine)
    test_engine.dispose() # engine manages db connections and connection pooling; disposing releases its pooled connections
    
@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session
        
@pytest.fixture
def client(engine):
    
    def override_get_session():
        with Session(engine) as session:
            yield session
            
    app.dependency_overrides[get_session] = override_get_session
    
    test_client = TestClient(app)
    yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def promoted_admin(session, make_user):
    user = make_user(username="test-user2")
    user.role = Role.ADMIN
    
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
    return user 

@pytest.fixture
def promoted_staff(session, make_user):
    user = make_user(username="test-user2")
    user.role = Role.STAFF
    
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
    return user 

@pytest.fixture
def make_user(session):
    def _make_user(username, password="testing"):
        user = UserDB(
            username = username,
            hashed_password=hash_password(password)
        )
        try:
            session.add(user)
            session.commit()
            session.refresh(user)
        except:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
        return user
    
    return _make_user

@pytest.fixture
def make_ticket(session):
    def _make_ticket(owner, title="example ticket", description="this is the description"):
        ticket = TicketDB(
            title=title,
            description=description,
            owner_id=owner.id
        )
        try:
            session.add(ticket)
            session.commit()
            session.refresh(ticket)
        except:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
        
    return _make_ticket

@pytest.fixture
def auth_headers():
    def _headers_for(user):
        token = create_token(data={"sub": user.username, "role": user.role}, expires_delta=set_token_expiry())
        return {"Authorization": f"Bearer {token}"}
    return _headers_for

@pytest.fixture
def normal_user(make_user): # receives the `session` fixture as a parameter: access to the temporary test db
    """ creates an admin account in the temporary database
    """
    return make_user(username="test_user")
    

@pytest.fixture
def admin_headers(promoted_admin, auth_headers): # generates JWT for the created admin
    return auth_headers(promoted_admin)

@pytest.fixture
def normal_user_headers(normal_user, auth_headers):
    return auth_headers(normal_user)

@pytest.fixture
def staff_headers(promoted_staff, auth_headers):
    return auth_headers(promoted_staff)

@pytest.fixture
def add_commit_refresh(session):
    def _add_commit_refresh(user):
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    return _add_commit_refresh
        
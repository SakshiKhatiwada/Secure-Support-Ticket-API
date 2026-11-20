# this file creates a temporary db, tables, sessions and test client

import pytest
from sqlmodel import SQLModel, Session, create_engine

from app.models.user import UserDB # registering purpose ko laagi ho, explicitly katai use nabhaye pani
from app.models.ticket import TicketDB

from app.main import app
from app.dependencies.session import get_session

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
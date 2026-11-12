from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

from app.routers.authentication import router as authentication_router
from app.routers.tickets import router as ticket_router
from app.dependencies.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    
app = FastAPI(title="Secure Support Ticket API", lifespan=lifespan)
app.include_router(authentication_router)
app.include_router(ticket_router)
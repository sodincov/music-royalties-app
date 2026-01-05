from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.settings import settings

# Создаём синхронный движок
engine = create_engine(settings.DATABASE_URL, echo=True)

# Сессия
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DBSessionDep = Annotated[Session, Depends(get_session)]
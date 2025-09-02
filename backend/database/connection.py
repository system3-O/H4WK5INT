from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import asyncio

from config.settings import settings

# Database engine
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,
    echo=settings.debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Metadata
metadata = MetaData()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def create_tables():
    """Create all tables"""
    from database.models import user, investigation, osint_result
    Base.metadata.create_all(bind=engine)
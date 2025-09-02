from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    investigations = relationship("Investigation", back_populates="owner")
    
class Investigation(Base):
    __tablename__ = "investigations"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    target = Column(String(500), nullable=False)  # Main target (email, domain, etc.)
    target_type = Column(String(50), nullable=False)  # email, domain, person, etc.
    status = Column(String(20), default="active")  # active, completed, archived
    priority = Column(String(10), default="medium")  # low, medium, high, critical
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="investigations")
    results = relationship("OSINTResult", back_populates="investigation")

class OSINTResult(Base):
    __tablename__ = "osint_results"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    module_name = Column(String(50), nullable=False)  # socmint, humint, imint, etc.
    sub_module = Column(String(50))  # specific tool within module
    query = Column(String(1000), nullable=False)
    result_type = Column(String(50), nullable=False)  # profile, domain, image, etc.
    data = Column(JSON)  # Main result data
    metadata = Column(JSON)  # Additional metadata
    confidence_score = Column(Integer, default=50)  # 0-100
    source_url = Column(String(1000))
    screenshot_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=False)
    
    # Relationships
    investigation = relationship("Investigation", back_populates="results")
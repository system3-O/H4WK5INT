from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import bcrypt as bcrypt_lib

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    role = Column(String(20), nullable=False, default='user')  # user, admin
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    investigations = relationship('Investigation', backref='user', lazy=True, cascade='all, delete-orphan')
    reports = relationship('Report', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt_lib.hashpw(password.encode('utf-8'), bcrypt_lib.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check password against hash"""
        return bcrypt_lib.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Investigation(db.Model):
    """Investigation model for organizing OSINT operations"""
    __tablename__ = 'investigations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    target = Column(String(500), nullable=True)  # Main target (person, domain, etc.)
    status = Column(String(20), nullable=False, default='active')  # active, completed, archived
    priority = Column(String(10), nullable=False, default='medium')  # low, medium, high, critical
    tags = Column(JSON, nullable=True)  # Array of tags
    metadata = Column(JSON, nullable=True)  # Additional metadata
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    osint_results = relationship('OSINTResult', backref='investigation', lazy=True, cascade='all, delete-orphan')
    reports = relationship('Report', backref='investigation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert investigation to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'target': self.target,
            'status': self.status,
            'priority': self.priority,
            'tags': self.tags or [],
            'metadata': self.metadata or {},
            'user_id': str(self.user_id),
            'results_count': len(self.osint_results),
            'reports_count': len(self.reports),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class OSINTResult(db.Model):
    """OSINT result model for storing module outputs"""
    __tablename__ = 'osint_results'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_name = Column(String(50), nullable=False)  # peopint, domain_intel, etc.
    operation_type = Column(String(100), nullable=False)  # username_search, whois_lookup, etc.
    query = Column(String(1000), nullable=False)  # Original query/target
    status = Column(String(20), nullable=False, default='pending')  # pending, completed, failed
    results = Column(JSON, nullable=True)  # Actual results data
    metadata = Column(JSON, nullable=True)  # Operation metadata (timing, source, etc.)
    error_message = Column(Text, nullable=True)  # Error details if failed
    investigation_id = Column(UUID(as_uuid=True), ForeignKey('investigations.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
    
    def to_dict(self):
        """Convert OSINT result to dictionary"""
        return {
            'id': str(self.id),
            'module_name': self.module_name,
            'operation_type': self.operation_type,
            'query': self.query,
            'status': self.status,
            'results': self.results or {},
            'metadata': self.metadata or {},
            'error_message': self.error_message,
            'investigation_id': str(self.investigation_id),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Report(db.Model):
    """Report model for generated reports"""
    __tablename__ = 'reports'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    report_type = Column(String(20), nullable=False)  # pdf, html, json, markdown, csv
    file_path = Column(String(500), nullable=True)  # Path to generated file
    file_size = Column(Integer, nullable=True)  # File size in bytes
    status = Column(String(20), nullable=False, default='generating')  # generating, completed, failed
    parameters = Column(JSON, nullable=True)  # Report generation parameters
    metadata = Column(JSON, nullable=True)  # Additional metadata
    error_message = Column(Text, nullable=True)  # Error details if failed
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    investigation_id = Column(UUID(as_uuid=True), ForeignKey('investigations.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
    
    def to_dict(self):
        """Convert report to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'report_type': self.report_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'status': self.status,
            'parameters': self.parameters or {},
            'metadata': self.metadata or {},
            'error_message': self.error_message,
            'user_id': str(self.user_id),
            'investigation_id': str(self.investigation_id) if self.investigation_id else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class BlacklistedToken(db.Model):
    """Blacklisted JWT tokens for logout functionality"""
    __tablename__ = 'blacklisted_tokens'
    
    id = Column(Integer, primary_key=True)
    jti = Column(String(36), nullable=False, unique=True)  # JWT ID
    token_type = Column(String(10), nullable=False)  # access or refresh
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    revoked_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    def is_expired(self):
        """Check if token is expired"""
        return datetime.now(timezone.utc) > self.expires_at
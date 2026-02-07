from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    passport_user_id = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    role = Column(String, default="user")
    status = Column(String, default="active")
    company_code = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

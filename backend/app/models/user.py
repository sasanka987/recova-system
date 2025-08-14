from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    status = Column(String(20), default="PENDING_APPROVAL")  # PENDING_APPROVAL, ACTIVE, INACTIVE, TERMINATED, SUSPENDED
    role_id = Column(Integer, ForeignKey("roles.id"))
    employee_code = Column(String(50), unique=True)
    phone_number = Column(String(20))
    department = Column(String(100))
    designation = Column(String(100))
    profile_image_path = Column(String(500))
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    approved_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    role = relationship("Role", back_populates="users")
    approver = relationship("User", remote_side=[id])
from sqlalchemy import Boolean, Column, DateTime, String, Enum, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType
import enum
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from sqlalchemy.sql import func
import uuid


class RoleEnum(enum.Enum):
    admin = "admin"
    editor = "editor"
    employee = "employee"
    suspended = "suspended"


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Enum(RoleEnum), unique=True, nullable=False)
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))  # ← UUID
    role = relationship("Role", back_populates="permissions")


class Department(Base):
    __tablename__ = "departments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    users = relationship("User", back_populates="department")


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    profile_picture = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    department_id = Column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True
    )  # ← FK vers department
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    verifications = relationship("EmailVerification", back_populates="user")
    department = relationship("Department", back_populates="users")

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return f"/static/profile_pictures/{self.profile_picture}"
        return None


class EmailVerification(Base):
    __tablename__ = "email_verifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )  # ← UUID
    token = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False, default="email_confirm")
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="verifications")

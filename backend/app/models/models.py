from sqlalchemy import Boolean, Column, DateTime, Integer, String, Enum, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType
import enum
from app.db.base import Base
from sqlalchemy.sql import func



class RoleEnum(enum.Enum):
    admin = "admin"
    editor = "editor"
    employee = "employee"


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(Enum(RoleEnum), unique=True, nullable=False)
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="permissions")



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(EmailType, unique=True, nullable=False, index=True)  # ← index pour les recherches rapides
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)                           # ← Boolean au lieu de Integer
    profile_picture = Column(String(255), nullable=True)                # ← limite la taille
    created_at = Column(DateTime, server_default=func.now())            # ← date de création
    updated_at = Column(DateTime, onupdate=func.now())                  # ← date de modification
    roles = relationship("Role", secondary=user_roles, back_populates="users")

    @property
    def profile_picture_url(self):
        if self.profile_picture: # type: ignore #
            return f"/static/profile_pictures/{self.profile_picture}"
        return None
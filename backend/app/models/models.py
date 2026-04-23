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
    is_active = Column(Boolean, default=False)                           # ← Boolean au lieu de Integer
    is_verified = Column(Boolean, default=False)                         # ← Boolean pour l'état de vérification
    profile_picture = Column(String(255), nullable=True)                # ← limite la taille
    created_at = Column(DateTime, server_default=func.now())            # ← date de création
    updated_at = Column(DateTime, onupdate=func.now())                  # ← date de modification
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    verifications = relationship("EmailVerification", back_populates="user", uselist=False)

    @property
    def profile_picture_url(self):
        if self.profile_picture: # type: ignore #
            return f"/static/profile_pictures/{self.profile_picture}"
        return None
    
class EmailVerification(Base):
    __tablename__ = "email_verifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False, default="email_confirm")
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="verifications")  # ← ajoute ça
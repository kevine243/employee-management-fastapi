from pydantic import BaseModel, EmailStr, model_validator, Field
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    username: str
    password: str = Field(min_length=6)
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("passwords do not match")
        return self


class UserRead(UserBase):
    id: UUID
    username: str
    is_active: bool

    model_config = {"from_attributes": True}


class UserDisplay(UserBase):
    id: UUID
    username: str
    profile_picture_url: str | None = None

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RoleRead(BaseModel):
    name: str

    model_config = {"from_attributes": True}


class DepartmentRead(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}


class UserDashboard(BaseModel):
    id: UUID
    username: str
    email: str
    is_active: bool
    is_verified: bool
    profile_picture_url: str | None
    created_at: datetime
    updated_at: datetime | None

    roles: list[RoleRead]
    department: DepartmentRead | None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: str
    email: EmailStr | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    profile_picture: str | None = None
    department_id: UUID | None = None

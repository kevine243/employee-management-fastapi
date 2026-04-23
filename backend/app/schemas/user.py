from pydantic import BaseModel, EmailStr, model_validator
from uuid import UUID, uuid4

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("passwords do not match")
        return self

class UserRead(UserBase):
    id: UUID
    is_active: bool

    model_config = {"from_attributes": True}

class UserDisplay(UserBase):
    id: UUID
    profile_picture_url: str | None = None

    model_config = {"from_attributes": True}


# ← Ajout pour le endpoint /login
class UserLogin(BaseModel):
    email: EmailStr
    password: str
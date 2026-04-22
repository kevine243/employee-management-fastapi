from pydantic import BaseModel, EmailStr, model_validator

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
    id: int
    is_active: bool

    model_config = {"from_attributes": True}

class UserDisplay(UserBase):
    id: int
    profile_picture_url: str | None = None

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int | None = None

# ← Ajout pour le endpoint /login
class UserLogin(BaseModel):
    email: EmailStr
    password: str
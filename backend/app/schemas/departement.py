from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime


class DepartmentBase(BaseModel):
    name: str  # ← id ne va pas dans Base


class DepartmentCreate(DepartmentBase):
    @field_validator("name")
    def validate_name(cls, v):
        if len(v) < 1:
            raise ValueError("Name too short")
        return v


class DepartmentRead(DepartmentBase):
    id: UUID  # ← id seulement en lecture
    created_at: datetime

    model_config = {"from_attributes": True}


class DepartmentUpdate(BaseModel):
    name: str | None = None

    @field_validator("name")
    def validate_name(cls, v):
        if v is None:
            return v

        if len(v) < 1:
            raise ValueError("Name too short")

        # if " " in v:
        #     raise ValueError("Username cannot contain spaces")

        return v  # ← optionnel pour update partiel

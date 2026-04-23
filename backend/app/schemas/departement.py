from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class DepartmentBase(BaseModel):
    name: str                          # ← id ne va pas dans Base

class DepartmentCreate(DepartmentBase):
    pass                               # ← juste name pour créer

class DepartmentRead(DepartmentBase):
    id: UUID                           # ← id seulement en lecture
    created_at: datetime

    model_config = {"from_attributes": True}

class DepartmentUpdate(BaseModel):
    name: str | None = None            # ← optionnel pour update partiel
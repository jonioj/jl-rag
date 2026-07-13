from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- User schemas ----------

class UserCreate(BaseModel):
    email: EmailStr


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_timestamp: datetime


class UserWithMessages(UserOut):
    messages: List["MessageOut"] = []


# ---------- Message schemas ----------

class MessageCreate(BaseModel):
    u_id: int
    questions: str
    answer: Optional[str] = None


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    u_id: int
    created_at: datetime
    questions: str
    answer: Optional[str] = None


UserWithMessages.model_rebuild()
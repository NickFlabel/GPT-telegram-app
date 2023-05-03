from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: str

    class Config:
        orm_mode = True


class MessageBase(BaseModel):
    content: str
    role: str

    class Config:
        orm_mode = True


class MessageCreate(MessageBase):
    conversation_id: int


class ConversationBase(BaseModel):
    name: str = 'Новый диалог'
    user_id: int

    class Config:
        orm_mode = True
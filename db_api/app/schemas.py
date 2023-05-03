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


class ConversationBase(BaseModel):
    name: str = 'Новый диалог'

    class Config:
        orm_mode = True

class ConversationRetrieve(ConversationBase):
    id: int

    class Config:
        orm_mode = True
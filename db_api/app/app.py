from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas
from .crud import User, Conversation, Message
from .db import get_db
from typing import List

app = FastAPI()


@app.get('/users', response_model=list[schemas.UserBase])
async def get_users(db: Session = Depends(get_db)):
    return User(db).get_users()


@app.get('/users/{user_id}', response_model=schemas.UserBase)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    return User(db).get_user_or_404(user_id=user_id)


@app.post('/users', response_model=schemas.UserBase, status_code=status.HTTP_201_CREATED)
async def create_user(new_user: schemas.UserBase, db: Session = Depends(get_db)):
    User(db).check_user_does_not_exists_or_400(user_id=new_user.id)
    return User(db).create_user(user=new_user)


@app.get('/users/{user_id}/conversations', response_model=List[schemas.ConversationRetrieve])
async def get_conversations(user_id: int, db: Session = Depends(get_db)):
    User(db).get_user_or_404(user_id=user_id)
    return Conversation(db).get_conversations(user_id=user_id)


@app.get('/users/{user_id}/conversations/{conversation_id}', response_model=schemas.ConversationRetrieve)
async def get_conversation(user_id: int, conversation_id: int, db: Session = Depends(get_db)):
    User(db).get_user_or_404(user_id=user_id)
    return Conversation(db).get_conversation_or_404(conversation_id=conversation_id, user_id=user_id)


@app.post('/users/{user_id}/conversations', response_model=schemas.ConversationRetrieve, status_code=status.HTTP_201_CREATED)
async def create_conversation(user_id: int, new_conversation: schemas.ConversationBase, db: Session = Depends(get_db)):
    User(db).get_user_or_404(user_id=user_id)
    return Conversation(db).create_conversation(conversation=new_conversation, user_id=user_id)


@app.get('/users/{user_id}/conversations/{conversation_id}/messages', response_model=List[schemas.MessageBase])
async def get_messages(user_id: int, conversation_id: int, db: Session = Depends(get_db)):
    User(db).get_user_or_404(user_id=user_id)
    Conversation(db).get_conversation_or_404(conversation_id=conversation_id, user_id=user_id)
    return Message(db).get_messages(conversation_id=conversation_id)


@app.post('/users/{user_id}/conversations/{conversation_id}/messages', response_model=schemas.MessageBase, status_code=status.HTTP_201_CREATED)
async def create_message(user_id: int, conversation_id: int, new_message: schemas.MessageBase, db: Session = Depends(get_db)):
    User(db).get_user_or_404(user_id=user_id)
    Conversation(db).get_conversation_or_404(conversation_id=conversation_id, user_id=user_id)
    return Message(db).create_message(message=new_message, conversation_id=conversation_id)

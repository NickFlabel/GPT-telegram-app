from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import crud, schemas
from .db import get_db

app = FastAPI()


@app.get('/users', response_model=list[schemas.UserBase])
async def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db=db)


@app.get('/users/{user_id}', response_model=schemas.UserBase)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return db_user


@app.post('/users', response_model=schemas.UserBase, status_code=status.HTTP_201_CREATED)
async def create_user(new_user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = crud.get_user(db=db, user_id=new_user.id)
    if db_user:
        raise HTTPException(status_code=400, detail='User already exists')
    return crud.create_user(db=db, user=new_user)


@app.post('/message', response_model=schemas.MessageBase,  status_code=status.HTTP_201_CREATED)
async def create_dialog(new_dialog: schemas.MessageCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db=db, user_id=new_dialog.user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return crud.create_message(db=db, dialog=new_dialog)


@app.post('/conversations', response_model=schemas.ConversationBase, status_code=status.HTTP_201_CREATED)
async def create_conversation(new_conversation: schemas.ConversationBase, db: Session = Depends(get_db)):
    db_user = crud.get_user(db=db, user_id=new_conversation.user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return crud.create_conversation(db=db, conversation=new_conversation)


@app.get('/conversations', response_model=schemas.ConversationBase)
async def get_conversations(user_id: int, db: Session = Depends(get_db)):
    return crud.get_conversations(db=db, user_id=user_id)
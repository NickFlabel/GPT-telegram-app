from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException


class User:
    def __init__(self, db: Session = None) -> None:
        self.db = db

    def get_user_or_404(self, user_id: int):
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_users(self):
        return self.db.query(models.User).all()

    def create_user(self, user: schemas.UserBase):
        db_user = models.User(**user.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def check_user_does_not_exists_or_400(self, user_id: int):
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            raise HTTPException(status_code=400, detail="User already exists")

class Conversation:
    def __init__(self, db: Session = None) -> None:
        self.db = db

    def get_conversations(self, user_id: int):
        return self.db.query(models.Conversation).filter(models.Conversation.user_id == user_id, models.Conversation.is_active == True).all()

    def get_conversation(self, conversation_id: int, user_id: int):
        return self.db.query(models.Conversation).filter(models.Conversation.id == conversation_id, models.Conversation.user_id == user_id, models.Conversation.is_active == True).first()

    def create_conversation(self, conversation: schemas.ConversationBase, user_id: int):
        conversation_dict = conversation.dict()
        db_user = self.db.query(models.User).filter(models.User.id == user_id).first()
        db_conversation = models.Conversation(**conversation_dict, user=db_user)
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        return db_conversation
    
    def get_conversation_or_404(self, conversation_id: int, user_id: int):
        conversation = self.db.query(models.Conversation).filter(models.Conversation.id == conversation_id, models.Conversation.user_id == user_id, models.Conversation.is_active == True).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    
    def delete_conversation(self, conversation_id: int, user_id: int):
        conversation = self.db.query(models.Conversation).filter(models.Conversation.id == conversation_id, models.Conversation.user_id == user_id).first()
        conversation.is_active = False
        self.db.add(conversation)
        self.db.commit()


class Message:
    def __init__(self, db: Session = None) -> None:
        self.db = db

    def get_messages(self, conversation_id: int):
        return self.db.query(models.Message).filter(models.Message.conversation_id == conversation_id).all()

    def create_message(self, message: schemas.MessageBase, conversation_id: int):
        message_dict = message.dict()
        db_conversation = self.db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
        db_message = models.Message(**message_dict, conversation=db_conversation)
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message
    
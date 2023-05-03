from sqlalchemy.orm import Session
from . import models, schemas
from .db import get_test_db
import random


class TestUser:
    def __init__(self, db: Session = None, id: int = None, first_name: str = None, last_name: str = None, username: str = None) -> None:
        self.user = None
        self.id = random.randrange(1000000, 9999999) if not id else id
        self.first_name = first_name if first_name else 'test'
        self.last_name = last_name if last_name else 'test'
        self.username = username if username else 'test'
        if not db:
            self.db = get_test_db().__next__()
        else:
            self.db = db

    def create_test_user(self):
        user = schemas.UserBase(id=self.id, first_name=self.first_name, last_name=self.last_name, username=self.username)
        db_user = models.User(**user.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        self.user = db_user
        return self
    
    def get_user(self):
        return self.user
    
    def get_user_id(self):
        return self.user.id
    
    def get_conversations(self):
        return self.user.conversations
    
    def get_username(self):
        return self.username
    

class TestConversation:

    def __init__(self, user_id: int, db: Session = None, id: int = None, name: str = None) -> None:
        self.conversation = None
        self.id = random.randrange(1000000, 9999999) if not id else id
        self.name = name if name else 'test'
        self.user_id = user_id
        if not db:
            self.db = get_test_db().__next__()
        else:
            self.db = db


    def create_test_conversation(self):
        conversation = schemas.ConversationBase(id=self.id, name=self.name, user_id=self.user_id)
        db_user = self.db.query(models.User).filter(models.User.id == conversation.dict().pop('user_id')).first()
        db_conversation = models.Conversation(**conversation.dict(), user=db_user)
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        self.conversation = db_conversation
        return self
    
    def get_conversation(self):
        return self.conversation
    
    def get_conversation_id(self):
        return self.conversation.id
    
    def get_messages(self):
        return self.conversation.messages


class TestMessage:

    def __init__(self, conversation_id: int, db: Session = None, id: int = None, content: str = None, role: str = None) -> None:
        self.message = None
        self.id = random.randrange(1000000, 9999999) if not id else id
        self.content = content if content else 'test'
        self.role = role if role else 'test'
        self.conversation_id = conversation_id
        if not db:
            self.db = get_test_db().__next__()
        else:
            self.db = db

    
    def create_test_message(self):
        message = schemas.MessageCreate(id=self.id, content=self.content, role=self.role, conversation_id=self.conversation_id)
        db_conv = self.db.query(models.Conversation).filter(models.Conversation.id == message.dict().pop('conversation_id')).first()
        db_message = models.Message(**message.dict(), conversation=db_conv)
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        self.message = db_message
        return self
    
    def get_message(self):
        return self.message
    
    def get_message_id(self):
        return self.message.id
    
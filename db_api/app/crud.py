from sqlalchemy.orm import Session
from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session):
    return db.query(models.User).all()


def create_user(db: Session, user: schemas.UserBase):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_conversations(db: Session, user_id: int):
    return db.query(models.Conversation).filter(models.Conversation.user_id == user_id).all()


def get_conversation(db: Session, conversation_id: int):
    return db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()


def create_conversation(db: Session, conversation: schemas.ConversationBase):
    conversation_dict = conversation.dict()
    db_user = db.query(models.User).filter(models.User.id == conversation_dict.pop('user_id')).first()
    db_conversation = models.Conversation(**conversation_dict, user=db_user)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


def create_message(db: Session, message: schemas.MessageCreate):
    message_dict = message.dict()
    db_user = db.query(models.User).filter(models.User.id == message_dict.pop('user_id')).first()
    conversation = db.query(models.Conversation).filter(models.Conversation.id == db_user.current_coversation_id).first()
    if not conversation:
        conversation = create_conversation(db=db, conversation=schemas.ConversationBase(user_id=db_user.id))
        db_user.current_coversation_id = conversation.id
        db.add(db_user)
    db_dialog = models.Message(**message_dict, user=db_user)
    db.add(db_dialog)
    db.commit()
    db.refresh(db_dialog)
    return db_dialog






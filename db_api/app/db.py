from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import dotenv
import os

dotenv.load_dotenv()

SQLALCHEMY_DATABASE_URL = f'{os.getenv("DB_DRIVER")}://{os.getenv("DB_USER")}:' \
                          f'{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:' \
                          f'{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
SQLALCHEMY_TEST_DATABASE_URL = f'{os.getenv("DB_DRIVER")}://{os.getenv("DB_USER")}:' \
                          f'{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:' \
                          f'{os.getenv("DB_PORT")}/{os.getenv("DB_TEST_NAME")}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_test_db():
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()

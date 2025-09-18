from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
import os


DB = os.getenv("DATABASE_NAME")
USER = os.getenv("USER_NAME")
HOST = os.getenv("HOST")
PASSWORD = os.getenv("PASSWORD")

import pymysql
pymysql.install_as_MySQLdb()

connection_string = f"mysql+mysqldb://{USER}:{PASSWORD}@{HOST}:3306/{DB}"
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
Base = declarative_base()
def init_db():
    from .user_model import User
    Base.metadata.create_all(engine)
@contextmanager
def get_db():
    session = Session()
    try:
        yield session
    finally:
        session.close()
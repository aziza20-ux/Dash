from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import String, Column, Integer
from .database import Base


class User(Base):
    __tablename__= 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    hash_password = Column(String(255), nullable=False)

    def set_hashpassword(self, user_password):
        self.hash_password = generate_password_hash(user_password)
    def check_password(self, entered_password):
        return check_password_hash(self.hash_password, entered_password)





import datetime

from sqlalchemy import Column, Integer, VARCHAR, DATE, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base


# Родительский класс
BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = 'user'
    # Telegram user id
    user_id = Column(Integer, unique=True, primary_key=True, autoincrement=False)
    username = Column(VARCHAR(32), unique=False, nullable=True)
    reg_date = Column(DATE, default=datetime.date.today())
    allowed = Column(BOOLEAN, default=False, nullable=False)
    quality = Column(VARCHAR(10), default='720p', nullable=False)

    def __str__(self) -> str:
        return f'<User: {self.user_id}>'

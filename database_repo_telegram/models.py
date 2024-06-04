from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text, create_engine)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class User(Base):
    """User scheme for storing the context of chatting"""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=False)
    gpt4o_lock = Column(Boolean, default=False)
    gpt4o_lock_timestamp = Column(DateTime, nullable=True)
    gpt4_lock = Column(Boolean, default=False)
    gpt4_lock_timestamp = Column(DateTime, nullable=True)
    messages = relationship(
        "Message", back_populates="user", cascade="all, delete-orphan"
    )


class Message(Base):
    """The message scheme for storing the user messages"""

    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    version = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="messages")

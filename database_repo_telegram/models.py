from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """User scheme for storing the context of chatting"""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=False)
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

    user = relationship("User", back_populates="messages")

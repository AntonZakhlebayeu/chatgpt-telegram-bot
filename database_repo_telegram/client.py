from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_repo_telegram.models import Base, Message, User


class DatabaseClient:
    """Database client for communicating with the sqlite"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseClient, cls).__new__(cls, *args, **kwargs)
            cls._instance._engine = create_engine("sqlite:///chatgpt_communication.db")
            Base.metadata.create_all(cls._instance._engine)
            cls._instance._Session = sessionmaker(bind=cls._instance._engine)
        return cls._instance

    def __init__(self) -> None:
        self.session = self._Session()

    def add_user(self, user_id: int) -> None:
        existing_user = self.session.query(User).filter_by(id=user_id).first()
        if existing_user:
            return

        user = User(id=user_id)
        self.session.add(user)
        self.session.commit()

    def delete_user(self, user_id: int) -> None:
        user = self.session.query(User).filter_by(id=user_id).first()
        if user:
            self.session.delete(user)
            self.session.commit()

    def add_message(self, user_id: int, role: str, content: str) -> None:
        message = Message(user_id=user_id, role=role, content=content)
        self.session.add(message)
        self.session.commit()

    def delete_messages_by_user_id(self, user_id: int) -> None:
        messages = self.session.query(Message).filter_by(user_id=user_id).all()
        for message in messages:
            self.session.delete(message)
        self.session.commit()

    def get_user_messages(self, user_id: int) -> list[Message]:
        user = self.session.query(User).filter_by(id=user_id).first()
        if user:
            return [{"role": msg.role, "content": msg.content} for msg in user.messages]
        return []


db_client = DatabaseClient()

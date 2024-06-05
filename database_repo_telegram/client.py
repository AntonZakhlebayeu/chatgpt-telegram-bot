from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_repo_telegram.models import Base, Message, User
from gpt_model import GPTVersion

# TODO: Add logger for this file


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

    def add_message(self, user_id: int, role: str, content: str, version: str) -> None:
        message = Message(user_id=user_id, role=role, content=content, version=version)
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

    def count_messages_in_timeframe(
        self, user_id: int, version: str, hours: int
    ) -> int:
        timeframe = datetime.utcnow() - timedelta(hours=hours)
        count = (
            self.session.query(Message)
            .filter(
                Message.user_id == user_id,
                Message.role == "user",
                Message.version == version,
                Message.timestamp >= timeframe,
            )
            .count()
        )
        return count

    def last_message_timestamp(self, user_id: int, version: str) -> datetime:
        last_message = (
            self.session.query(Message)
            .filter(Message.user_id == user_id, Message.version == version)
            .order_by(Message.timestamp.desc())
            .first()
        )
        return last_message.timestamp if last_message else None

    def set_lock_for_sending_messages(self, user_id: int, version: str) -> None:
        user = self.session.query(User).filter_by(id=user_id).first()
        if version == GPTVersion.GPT_4:
            user.gpt4_lock = True
            last_message_time = self.last_message_timestamp(user_id, version)
            user.gpt4_lock_timestamp = last_message_time + timedelta(hours=6)
        elif version == GPTVersion.GPT_4o:
            user.gpt4o_lock = True
            last_message_time = self.last_message_timestamp(user_id, version)
            user.gpt4o_lock_timestamp = last_message_time + timedelta(minutes=6)
        self.session.commit()

    # TODO: Refactor this function, make it small and less responsible
    def can_send_message(self, user_id: int, version: str) -> bool:
        user = self.session.query(User).filter_by(id=user_id).first()

        if version == GPTVersion.GPT_4 and user.gpt4_lock:
            if user.gpt4_lock_timestamp <= datetime.utcnow():
                user.gpt4_lock = False
                self.session.commit()
                return True
            else:
                return False
        elif version == GPTVersion.GPT_4o and user.gpt4o_lock:
            if user.gpt4o_lock_timestamp <= datetime.utcnow():
                user.gpt4o_lock = False
                self.session.commit()
                return True
            else:
                return False
        elif version == GPTVersion.GPT_4 and not (user.gpt4_lock or user.gpt4o_lock):
            have_ability = self.count_messages_in_timeframe(user_id, version, 5) < 3
            if not have_ability:
                self.set_lock_for_sending_messages(user_id, version)
            return have_ability
        elif version == GPTVersion.GPT_4o and not (user.gpt4_lock or user.gpt4o_lock):
            have_ability = self.count_messages_in_timeframe(user_id, version, 4) < 10
            if not have_ability:
                self.set_lock_for_sending_messages(user_id, version)
            return have_ability
        return True

    def get_availability_to_use_version(
        self, user_id: int, version: str
    ) -> datetime.timestamp:
        user = self.session.query(User).filter_by(id=user_id).first()
        if version == GPTVersion.GPT_4:
            return user.gpt4_lock_timestamp.strftime("%H:%M")
        elif version == GPTVersion.GPT_4o:
            return user.gpt4o_lock_timestamp.strftime("%H:%M")


db_client = DatabaseClient()

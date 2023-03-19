from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import relationship
import os
import time
import threading


class Base(DeclarativeBase):
    pass


class UserData(Base):
    __tablename__ = 'userdata'

    user_id: Mapped[str] = mapped_column(primary_key=True)
    current_tokens: Mapped[int]
    max_tokens: Mapped[int]
    has_upgraded: Mapped[bool]
    system_message: Mapped[str]


db_path = 'sqlite:///user_data.db'


def db_connect(_db_path: str):
    new_engine = create_engine(_db_path, echo=True)
    if not os.path.isfile(_db_path.replace('sqlite:///', '')):
        print(os.path.isfile(_db_path.replace('sqlite:///', '')))
        table = Base.metadata.create_all(new_engine)
    return Session(new_engine)


def get_system_message(user_id: str):
    with db_connect(db_path) as session:
        user_data = session.query(UserData).filter_by(user_id=user_id).first()
        return user_data.system_message


def save_data_tables(backup_file_path: str = 'backup.txt'):
    data = copy_data()
    with open(backup_file_path, 'w') as f:
        for user in data.items():
            for item in user[1]:
                f.write(str(item) + ':')
            f.write('\n')


def update_user_settings(user_id: str, _system_message: str):
    with db_connect(db_path) as session:
        user_data = session.query(UserData).filter_by(user_id=user_id).first()
        user_data.system_message = _system_message
        session.commit()


def backup_auto():
    def backup_loop():
        while True:
            save_data_tables()
            time.sleep(43200)
    threading.Thread(target=backup_loop).start()


def copy_data() -> dict:
    backup_data = {}

    with db_connect(db_path) as session:
        users = session.query(UserData).all()

    for user in users:
        backup_data[user.user_id] = (user.user_id, user.current_tokens, user.max_tokens, user.has_upgraded)

    return backup_data


def user_exists(user_id: str) -> bool:
    with db_connect(db_path) as session:
        if session.query(UserData).filter_by(user_id=user_id).first() is not None:
            return True
        return False


def user_create(user_id: str):
    with db_connect(db_path) as session:
        session.add(UserData(
            user_id=user_id,
            current_tokens=0,
            max_tokens=50000,
            has_upgraded=False,
            system_message=''
        ))
        session.commit()


def append_user_usage(user_id: str, tokens_used: int):
    with db_connect(db_path) as session:
        user_data = session.query(UserData).filter_by(user_id=user_id).first()
        user_data.current_tokens += tokens_used
        session.commit()


def get_user_usage(user_id: str) -> dict:
    with db_connect(db_path) as session:
        user_data = session.query(UserData).filter_by(user_id=user_id).first()
        return {'current_usage': user_data.current_tokens, 'max_usage': user_data.max_tokens}


def usage_available(user_id: str) -> bool:
    usage = get_user_usage(user_id)
    if usage['current_usage'] < usage['max_usage']:
        return True
    return False


def available_usage(user_id: str) -> bool:
    with db_connect(db_path) as session:
        user_data = session.query(UserData).filter_by(user_id=user_id).first()
        if user_data.current_tokens < user_data.max_tokens:
            return True
        return False


def upgrade_account(user_id: str, upgrade_type: int):
    with db_connect(db_path) as session:
        user_data = session.query(UserData).filter_by(user_id=user_id).first()
        user_data.has_upgraded = True

        if upgrade_type == 5:
            user_data.max_tokens += 350000

        if upgrade_type == 10:
            user_data.max_tokens += 800000


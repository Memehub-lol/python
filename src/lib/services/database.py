import os
from enum import Enum
from multiprocessing import cpu_count
from typing import Callable

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session, sessionmaker
from src.lib.environment import Environment


class Database(Enum):
    SITE = "SITE"
    TRAINING = "TRAINING"


databases = {Database.SITE: {"protocol": "postgresql",
                             "user": os.environ["DATABASE_USER"],
                             "password": os.environ["DATABASE_PASSWORD"],
                             "host": "sitedata" if Environment.is_docker else "127.0.0.1",
                             "port": 5432,
                             "db_name": "postgres"},
             Database.TRAINING: {"protocol": "postgresql",
                                 "user": os.environ["DATABASE_USER"],
                                 "password": os.environ["DATABASE_PASSWORD"],
                                 "host": "trainingdata" if Environment.is_docker else "127.0.0.1",
                                 "port": 5432 if Environment.is_docker else 5433,
                                 "db_name": "postgres"}}


class DatabaseConfig:
    @classmethod
    def url(cls, database: Database):
        config = databases[database]
        return f"{config['protocol']}://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['db_name']}"


pool_size = cpu_count() + 2

training_engine = create_engine(DatabaseConfig.url(Database.TRAINING), pool_size=pool_size, future=True)
training_session_maker: Callable[..., Session] = sessionmaker(bind=training_engine, future=True)

site_engine = create_engine(DatabaseConfig.url(Database.SITE), pool_size=pool_size, future=True)
site_session_maker: Callable[..., Session] = sessionmaker(bind=site_engine, future=True)

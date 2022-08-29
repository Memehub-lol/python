import os
from enum import Enum
from multiprocessing import cpu_count
from typing import Callable

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session, sessionmaker


class Database(Enum):
    SITE = "SITE"
    TRAINING = "TRAINING"

    def get_config(self):
        return {
            Database.SITE: ("postgresql",
                            os.environ["POSTGRES_USER"],
                            os.environ["POSTGRES_PASSWORD"],
                            os.environ["POSTGRES_HOST"],
                            os.environ["POSTGRES_PORT"],
                            os.environ["POSTGRES_DB"]),
            Database.TRAINING: ("postgresql",
                                os.environ["POSTGRES_USER"],
                                os.environ["POSTGRES_PASSWORD"],
                                "trainingdata",
                                os.environ["POSTGRES_PORT"],
                                os.environ["POSTGRES_DB"])
        }[self]

    def url(self):
        protocol, user, password, host, port, db_Name = self.get_config()
        return f"{protocol}://{user}:{password}@{host}:{port}/{db_Name}"


pool_size = cpu_count() + 2

training_engine = create_engine(Database.TRAINING.url(), pool_size=pool_size, future=True)
training_session_maker: Callable[..., Session] = sessionmaker(bind=training_engine, future=True)

site_engine = create_engine(Database.SITE.url(), pool_size=pool_size, future=True)
site_session_maker: Callable[..., Session] = sessionmaker(bind=site_engine, future=True)

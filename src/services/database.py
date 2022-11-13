from multiprocessing import cpu_count
from typing import Callable

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session, sessionmaker
from src.enums.e_database import EDatabase
from src.services.environment import Environment

pool_size = cpu_count() + 2

if Environment.IS_LOCAL:
    training_engine = create_engine(EDatabase.TRAINING.url(), pool_size=pool_size, future=True)
    training_session_maker: Callable[..., Session] = sessionmaker(bind=training_engine, future=True)
else:
    training_engine, training_session_maker = None, None  # type: ignore training db only exists in local dev

site_engine = create_engine(EDatabase.SITE.url(), pool_size=pool_size, future=True)
site_session_maker: Callable[..., Session] = sessionmaker(bind=site_engine, future=True)

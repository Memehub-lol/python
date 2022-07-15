from typing import Callable, ClassVar, Type

from sqlalchemy import func, select
from sqlalchemy.orm.session import Session
from src.lib.services.database import site_session_maker
from src.modules.base import BaseRepo
from src.modules.generated.site_dataclasses import \
    Templates as TemplatesDataclass
from src.modules.generated.site_tables import Templates


class TemplateRepo(BaseRepo[TemplatesDataclass]):
    Dataclass: ClassVar[Type[TemplatesDataclass]] = TemplatesDataclass
    Table: ClassVar[Type[Templates]] = Templates
    sessionmaker: ClassVar[Callable[..., Session]] = site_session_maker

    @classmethod
    def count(cls) -> int:
        with site_session_maker() as session:
            return session.scalar(select(func.count(Templates.name.distinct())))

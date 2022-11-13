from typing import Callable, ClassVar, Type

from src.generated.site_dataclasses import \
    ImgflipTemplates as ImgflipTemplatesDataclass
from src.generated.site_tables import ImgflipTemplates
from sqlalchemy import func, select
from sqlalchemy.orm.session import Session
from src.modules.base import BaseRepo
from src.services.database import site_session_maker


class TemplateRepo(BaseRepo):
    Dataclass: ClassVar[Type[ImgflipTemplatesDataclass]] = ImgflipTemplatesDataclass
    Table: ClassVar[Type[ImgflipTemplates]] = ImgflipTemplates
    sessionmaker: ClassVar[Callable[..., Session]] = site_session_maker

    @classmethod
    def count(cls) -> int:
        with site_session_maker() as session:
            return session.scalar(select(func.count(ImgflipTemplates.name.distinct())))

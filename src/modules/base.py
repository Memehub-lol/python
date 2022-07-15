
from typing import Any, Callable, ClassVar, Dict, Generic, List, Type, TypeVar

from sqlalchemy.orm.session import Session
from sqlalchemy.sql.schema import Table

ReturnType = TypeVar("ReturnType")
Repo = TypeVar("Repo")


class BaseRepo(Generic[Repo]):
    Dataclass: ClassVar[type]
    Table: ClassVar[Type[Table]]
    sessionmaker: ClassVar[Callable[..., Session]]

    @classmethod
    def get_column_names(cls) -> List[str]:
        return [c.name for c in getattr(cls, "__table__").columns]

    def json(self, db_dump: bool = False) -> Dict[str, Any]:
        return {column: getattr(self, column) for column in self.get_column_names()}

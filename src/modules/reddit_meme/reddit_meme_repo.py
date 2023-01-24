from datetime import datetime
from typing import Callable, ClassVar, Optional, Type
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.sql.operators import ColumnOperators

from src.generated.site_tables import RedditMemes
from src.services.database import site_session_maker


class RedditMemeRepo:
    subreddit_list: ClassVar[list[str]] = ["dankmemes", "memes"]

    @classmethod
    def max_dt(cls, *where_clause: ColumnOperators) -> Optional[datetime]:
        with site_session_maker() as session:
            return session.execute(select(func.max(RedditMemes.created_at)).where(*where_clause)).scalar()

    @classmethod
    def min_dt(cls, *where_clause: ColumnOperators) -> Optional[datetime]:
        with site_session_maker() as session:
            return session.execute(select(func.min(RedditMemes.created_at)).where(*where_clause)).scalar()

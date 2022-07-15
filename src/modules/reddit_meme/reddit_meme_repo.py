from datetime import datetime
from typing import Any, Callable, ClassVar, Optional, Type
from uuid import uuid4

from praw.reddit import Submission
from sqlalchemy import Boolean, func, select
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.operators import ColumnOperators
from src.lib.services.database import site_session_maker
from src.modules.base import BaseRepo
from src.modules.generated.site_dataclasses import \
    RedditMemes as RedditMemesDataclass
from src.modules.generated.site_tables import RedditMemes, Redditors


class RedditMemeRepo(BaseRepo[RedditMemesDataclass]):
    Dataclass: ClassVar[Type[RedditMemesDataclass]] = RedditMemesDataclass
    Table: ClassVar[Type[RedditMemes]] = RedditMemes
    sessionmaker: ClassVar[Callable[..., Session]] = site_session_maker
    subreddit_list: ClassVar[list[str]] = ["dankmemes", "memes"]

    @classmethod
    def denorm_reddit_submission(cls, submission: Submission):
        if (username := str(submission.author)) == "None":
            return
        return cls.Dataclass(id=uuid4().hex,
                             idx=0,
                             reddit_id=submission.id,
                             title=submission.title,
                             username=username,
                             timestamp=submission.created_utc,
                             created_at=datetime.fromtimestamp(submission.created_utc),
                             url=submission.url,
                             upvote_ratio=submission.upvote_ratio,
                             upvotes=submission.score,
                             downvotes=round(submission.score / submission.upvote_ratio)
                             - submission.score,
                             num_comments=submission.num_comments,
                             subreddit=str(submission.subreddit))

    @classmethod
    def max_ts(cls, *where_clause: ColumnOperators) -> Optional[float]:
        with cls.sessionmaker() as session:
            return session.execute(select(func.max(cls.Table.timestamp)).where(*where_clause)).scalar()

    @classmethod
    def min_ts(cls, *where_clause: ColumnOperators) -> Optional[float]:
        with cls.sessionmaker() as session:
            return session.execute(select(func.min(cls.Table.timestamp)).where(*where_clause)).scalar()

    @classmethod
    def fill_redditor_id(cls, memes: list[RedditMemesDataclass]):
        usernames = [meme.username for meme in memes]
        with cls.sessionmaker() as session:
            redditors = session.execute(select(Redditors).where(Redditors.username.in_(usernames))).scalars().all()
        new_redditors: list[Redditors] = []
        username_to_redditor = {redditor.username: redditor for redditor in redditors}
        for meme in memes:
            if meme.username not in username_to_redditor:
                new_redditor = Redditors(username=meme.username, id=uuid4().hex)
                username_to_redditor[meme.username] = new_redditor
                new_redditors.append(new_redditor)
            meme.redditor_id = username_to_redditor[meme.username].id
        return new_redditors

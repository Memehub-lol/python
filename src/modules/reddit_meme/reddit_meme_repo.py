from datetime import datetime
from typing import Callable, ClassVar, Optional, Type
from uuid import uuid4

from praw.reddit import Submission
from sqlalchemy import func, select
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.operators import ColumnOperators
from src.generated.site_dataclasses import RedditMemes as RedditMemesDataclass
from src.generated.site_tables import RedditMemes, Redditors
from src.modules.base import BaseRepo
from src.services.database import site_session_maker


class RedditMemeRepo(BaseRepo):
    Dataclass: ClassVar[Type[RedditMemesDataclass]] = RedditMemesDataclass
    Table: ClassVar[Type[RedditMemes]] = RedditMemes
    sessionmaker: ClassVar[Callable[..., Session]] = site_session_maker
    subreddit_list: ClassVar[list[str]] = ["dankmemes", "memes"]

    @classmethod
    def denorm_reddit_submission(cls, submission: Submission):
        if (username := str(submission.author)) == "None":
            return
        return username, cls.Table(id=uuid4().hex,
                                   idx=0,
                                   reddit_id=submission.id,
                                   title=submission.title,
                                   created_at=datetime.fromtimestamp(submission.created_utc),
                                   url=submission.url,
                                   upvote_ratio=submission.upvote_ratio,
                                   upvotes=submission.score,
                                   downvotes=round(submission.score / submission.upvote_ratio)
                                   - submission.score,
                                   num_comments=submission.num_comments,
                                   subreddit=str(submission.subreddit))

    @classmethod
    def max_dt(cls, *where_clause: ColumnOperators) -> Optional[datetime]:
        with cls.sessionmaker() as session:
            return session.execute(select(func.max(cls.Table.created_at)).where(*where_clause)).scalar()

    @classmethod
    def min_dt(cls, *where_clause: ColumnOperators) -> Optional[datetime]:
        with cls.sessionmaker() as session:
            return session.execute(select(func.min(cls.Table.created_at)).where(*where_clause)).scalar()

    @classmethod
    def fill_redditor_id(cls, memes: list[RedditMemesDataclass], usernames: list[str]):
        with cls.sessionmaker() as session:
            redditors = session.execute(select(Redditors).where(Redditors.username.in_(usernames))).scalars().all()
        new_redditors: list[Redditors] = []
        username_to_redditor = {redditor.username: redditor for redditor in redditors}
        for idx, meme in enumerate(memes):
            username = usernames[idx]
            if username not in username_to_redditor:
                new_redditor = Redditors(username=username, id=uuid4().hex)
                username_to_redditor[username] = new_redditor
                new_redditors.append(new_redditor)
            meme.redditor_id = username_to_redditor[username].id
        return new_redditors

import json
import random
from datetime import datetime, timedelta
from typing import ClassVar, Iterator, TypedDict, cast

import arrow
import pandas as pd
from praw.reddit import Reddit, Submission
from sqlalchemy import and_, func, select
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import and_
from src.lib import logger, utils
from src.lib.environment import Environment
from src.lib.services.database import site_session_maker
from src.modules.generated.site_tables import RedditMemes
from src.modules.reddit_meme.reddit_meme_repo import RedditMemeRepo


def get_reddit_objs():
    return [Reddit(**json.loads(oauth)) for oauth in Environment.get_reddit_oauths()]


class PushshiftParams(TypedDict):
    query_limit: int
    batch_size: int
    uri: str


class RedditMemeScrapper:
    reddit_objs: ClassVar[list[Reddit]] = get_reddit_objs()
    record_percentile_every_x_hours: ClassVar[int] = 24
    pushshift: ClassVar[PushshiftParams] = {"query_limit": 100,
                                            "batch_size": 1_000,
                                            "uri": r"https://api.pushshift.io/reddit/search/submission?subreddit={}&after={}&before={}&size={}"}

    @classmethod
    def _praw_by_submission_id(cls, submission_id: str):
        try:
            submission: Submission = random.choice(cls.reddit_objs).submission(id=submission_id)
            if not submission.stickied:
                if any(submission.url.endswith(filetype)for filetype in [".jpg", ".jpeg", ".png"]):
                    return RedditMemeRepo.denorm_reddit_submission(submission)
        except Exception as e:
            logger.error("PRAW: %s", e)

    @classmethod
    def _query_pushshift(cls, subreddit: str, grace_period: int = 1) -> Iterator[list[str]]:
        end_at = int((datetime.utcnow().replace(second=0, minute=0) - timedelta(days=grace_period)).timestamp())
        with site_session_maker() as session:
            maybe_start_at = session.execute(select(func.max(RedditMemes.timestamp)).where(RedditMemes.subreddit == subreddit)).scalar()
        start_at = maybe_start_at or int((datetime.utcnow().replace(hour=0, second=0, minute=0) - timedelta(days=31)).timestamp())
        done = False
        logger.info("PushShift Ids: from %s to %s", datetime.fromtimestamp(start_at), datetime.fromtimestamp(end_at))
        while not done:
            post_ids: list[str] = []
            while not done and len(post_ids) < cls.pushshift["batch_size"]:
                url = cls.pushshift["uri"].format(subreddit, start_at, end_at, cls.pushshift["query_limit"])
                if not (raw := utils.make_request(url)):
                    break
                if not (posts := raw["data"]):
                    done = True
                    break
                done = done or len(posts) != cls.pushshift["query_limit"]
                post_ids.extend(post["id"] for post in posts)
                start_at: int = posts[-1]["created_utc"] - 1
            yield post_ids

    @classmethod
    def praw_memes(cls, verbose: bool = True, multi: bool = True, use_billard: bool = True):
        for subreddit in RedditMemeRepo.subreddit_list:
            logger.info("Scrapping: %s", subreddit)
            for ids in cls._query_pushshift(subreddit):
                raw_memes = utils.process(cls._praw_by_submission_id, set(ids), verbose=verbose, use_billard=use_billard, multi=multi)
                with site_session_maker() as session:
                    current_urls = [meme.url for meme in raw_memes]
                    dup_urls: list[str] = session.execute(select(RedditMemes.url).filter(RedditMemes.url.in_(current_urls))).scalars().all()
                raw_memes = list({meme.url: meme for meme in raw_memes if meme.url not in dup_urls}.values())
                new_redditors = RedditMemeRepo.fill_redditor_id(raw_memes)
                with RedditMemeRepo.sessionmaker() as session:
                    session.add_all(new_redditors)
                    session.add_all(raw_memes)
                    session.commit()
                logger.info("num_ids_scraped: %s", len(ids))

    @classmethod
    def calc_percentiles(cls, verbose: bool = True):
        for subreddit in RedditMemeRepo.subreddit_list:
            cls._calc_percentile_sub(subreddit, verbose)

    @classmethod
    def _calc_percentile_sub(cls, subreddit: str, verbose: bool = True):
        subreddit_clause = RedditMemes.subreddit == subreddit
        clause = and_(subreddit_clause, RedditMemes.percentile != None)
        timestamp = RedditMemeRepo.max_ts(clause) or RedditMemeRepo.min_ts(subreddit_clause)
        if not timestamp:
            return
        max_ts = arrow.get(timestamp).ceil("hour").shift(days=1)
        clause = and_(subreddit_clause, RedditMemes.created_at > max_ts.shift(days=-1).datetime)
        with RedditMemeRepo.sessionmaker() as session:
            reddit_id_to_meme = {meme.reddit_id: meme for meme in session.execute(select(RedditMemes).where(clause)).scalars()}
            stmt = str(select(RedditMemes.reddit_id, RedditMemes.upvotes, RedditMemes.created_at, RedditMemes.percentile).where(clause))
            df = pd.read_sql(stmt, session.bind, columns=["reddit_id", "upvotes", "created_at", "percentile"],)
            while max_ts < arrow.utcnow().floor("hour").shift(days=-1, seconds=-1):
                if verbose:
                    logger.info(max_ts.format("YYYY-MM-DD HH:mm:ss"))
                mask = df["created_at"].gt(max_ts.naive) & df["created_at"].lt(max_ts.shift(days=1).naive)
                frame = df.loc[mask, ["upvotes", "reddit_id", "percentile"]]
                frame["percentile"] = frame["upvotes"].rank(pct=True)
                for _, row in frame.loc[frame["percentile"].isna()].iterrows():
                    reddit_id = cast(str, row["reddit_id"])
                    percentile = cast(float, row["percentile"])
                    reddit_id_to_meme[reddit_id].percentile = percentile
                session.commit()
                max_ts = max_ts.shift(hours=cls.record_percentile_every_x_hours)

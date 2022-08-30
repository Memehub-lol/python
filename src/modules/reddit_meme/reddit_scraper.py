import json
import random
from datetime import datetime, timedelta
from typing import ClassVar, Iterator, TypedDict

import arrow
import numpy as np
import pandas as pd
from praw.reddit import Reddit, Submission
from sqlalchemy import and_, func, select
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import and_
from src.lib import logger, utils
from src.services.environment import Environment
from src.services.database import site_session_maker
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
    pushshift: ClassVar[PushshiftParams] = {"query_limit": 100,
                                            "batch_size": 1_000,
                                            "uri": r"https://api.pushshift.io/reddit/search/submission?subreddit={}&after={}&before={}&size={}"}

    @classmethod
    def _praw_by_submission_id(cls, submission_id: str):
        try:
            submission: Submission = random.choice(cls.reddit_objs).submission(id=submission_id)
            if not submission.stickied:
                if any(submission.url.endswith(filetype) for filetype in [".jpg", ".jpeg", ".png"]):
                    return RedditMemeRepo.denorm_reddit_submission(submission)
        except Exception as e:
            logger.error("PRAW: %s", e)

    @classmethod
    def _query_pushshift(cls, subreddit: str, grace_period: int = 1) -> Iterator[list[str]]:
        end_at = int((datetime.utcnow().replace(second=0, minute=0) - timedelta(days=grace_period)).timestamp())
        with site_session_maker() as session:
            maybe_start_at = session.execute(select(func.max(RedditMemes.timestamp)).where(RedditMemes.subreddit == subreddit)).scalar()
        start_at = maybe_start_at or int((datetime.utcnow().replace(hour=0, second=0, minute=0) - timedelta(days=62)).timestamp())
        logger.info("PushShift Ids: from %s to %s", datetime.fromtimestamp(start_at), datetime.fromtimestamp(end_at))
        done = False
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
    def _calc_percentile_sub(cls, subreddit: str, verbose: bool = True, rank_over_days: int = 30):
        subreddit_clause = RedditMemes.subreddit == subreddit
        percentile_subreddit_clause = and_(subreddit_clause, RedditMemes.percentile != None)
        max_ts = RedditMemeRepo.max_ts(subreddit_clause)
        min_ts = RedditMemeRepo.min_ts(subreddit_clause)
        timestamp = RedditMemeRepo.max_ts(percentile_subreddit_clause) or min_ts
        if not timestamp or not max_ts or not min_ts or timedelta(seconds=max_ts-min_ts) < timedelta(days=rank_over_days):
            return
        start_dt = arrow.get(timestamp).floor("hour")
        clause = and_(subreddit_clause, RedditMemes.created_at > start_dt.datetime)
        with RedditMemeRepo.sessionmaker() as session:
            reddit_id_to_meme = {meme.reddit_id: meme for meme in session.execute(select(RedditMemes).where(clause)).scalars()}
            df = pd.DataFrame.from_records([{"reddit_id": meme.reddit_id,
                                             "upvotes": meme.upvotes,
                                             "created_at": meme.created_at,
                                             "percentile": meme.percentile} for meme in reddit_id_to_meme.values()])
            end_ts = arrow.utcnow().floor("hour").shift(days=-1, seconds=-1)
            while start_dt.shift(days=rank_over_days) < end_ts:
                create_at_col = df["created_at"].astype(np.int64).divide(1_000_000_000)
                mask_start_ranking = create_at_col.gt(start_dt.timestamp())
                mask_end_ranking = create_at_col.lt(start_dt.shift(days=rank_over_days).timestamp())
                frame = df.loc[mask_start_ranking & mask_end_ranking, ["upvotes", "reddit_id", "percentile"]]
                frame["percentile"] = frame["upvotes"].rank(pct=True)
                mask_end_window = create_at_col.lt(start_dt.shift(days=rank_over_days//2+1).timestamp())
                for _, row in frame.loc[mask_end_window].iterrows():
                    meme = reddit_id_to_meme[row["reddit_id"]]
                    if not meme.percentile:
                        meme.percentile = row["percentile"]
                session.commit()
                start_dt = start_dt.shift(days=1)

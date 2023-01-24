import json
import random
from datetime import datetime, timedelta
from typing import Iterator, cast
from urllib.parse import urlencode
from uuid import uuid4

import arrow
import numpy as np
import pandas as pd
from praw.reddit import Reddit, Submission
from sqlalchemy import and_, func, select
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import and_

from src.generated.site_tables import RedditMemes, Redditors
from src.lib import logger, utils
from src.lib.make_request import make_request
from src.modules.reddit_meme.reddit_meme_repo import RedditMemeRepo
from src.services.database import site_session_maker
from src.services.environment import Environment

reddit_objs = [Reddit(**json.loads(oauth)) for oauth in Environment.get_reddit_oauths()]


def _fill_redditor_id(memes: list[RedditMemes], usernames: list[str]):
    with site_session_maker() as session:
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


def _praw_by_submission_id(submission_id: str):
    try:
        submission: Submission = random.choice(reddit_objs).submission(id=submission_id)
        username = str(submission.author)
        if (not submission.stickied and submission.url and any(submission.url.endswith(filetype) for filetype in [".jpg", ".jpeg", ".png"]) and username != "None"):
            return username, RedditMemes(id=uuid4().hex,
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
    except Exception as e:
        logger.error("PRAW: %s", e)


def _query_pushshift(subreddit: str, grace_period: int = 7) -> Iterator[list[str]]:
    end_at = int((datetime.utcnow().replace(second=0, minute=0) - timedelta(days=grace_period)).timestamp())
    with site_session_maker() as session:
        maybe_start_at = session.execute(select(func.max(RedditMemes.created_at)).where(RedditMemes.subreddit == subreddit)).scalar()
    if maybe_start_at:
        start_at = int(maybe_start_at.timestamp())
    else:
        start_at = int((datetime.utcnow().replace(hour=0, second=0, minute=0) - timedelta(days=247)).timestamp())
    logger.info("PushShift Ids: from %s to %s", datetime.fromtimestamp(start_at), datetime.fromtimestamp(end_at))
    url = "https://api.pushshift.io/reddit/search/submission?"
    done = False
    batch_size = 1_000
    while not done:
        post_ids: list[str] = []
        while not done and len(post_ids) < batch_size:
            raw = make_request(url + urlencode({"subreddit": subreddit,
                                                "after": start_at,
                                                "before": end_at,
                                                "size": 100}))
            if not raw:
                break
            if not (posts := raw["data"]):
                done = True
                break
            if (end_at := min(post["created_utc"] for post in posts)) <= start_at:
                done = True
            post_ids.extend(post["id"] for post in posts)
            logger.info("Ids: from %s to %s", datetime.fromtimestamp(posts[0]["created_utc"]), datetime.fromtimestamp(posts[-1]["created_utc"]))
        yield post_ids


def praw_memes(*, verbose: bool = True, multi: bool = True, use_billard: bool = True):
    for subreddit in RedditMemeRepo.subreddit_list:
        logger.info("Scrapping: %s", subreddit)
        for ids in _query_pushshift(subreddit):
            processed = utils.process(_praw_by_submission_id, set(ids), verbose=verbose, use_billard=use_billard, multi=multi)
            usernames, raw_memes = cast(tuple[list[str], list[RedditMemes]], list(zip(*processed)))
            new_redditors = _fill_redditor_id(raw_memes, usernames)
            current_urls = [meme.url for meme in raw_memes]
            with site_session_maker() as session:
                dup_urls: list[str] = session.execute(select(RedditMemes.url).filter(RedditMemes.url.in_(current_urls))).scalars().all()
            raw_memes = list({meme.url: meme for meme in raw_memes if meme.url not in dup_urls}.values())
            with site_session_maker() as session:
                session.add_all(new_redditors)
                session.add_all(raw_memes)
                session.commit()
            logger.info("num_ids_scraped: %s", len(ids))
            logger.info("num_ids_scraped_dedup: %s", len(set(ids)))
            logger.info("num_submissions: %s", len(processed))
            logger.info("num_raw_memes: %s", len(raw_memes))


def calc_percentiles(*, rank_over_days: int = 30):
    for subreddit in RedditMemeRepo.subreddit_list:
        subreddit_clause = RedditMemes.subreddit == subreddit
        max_dt = RedditMemeRepo.max_dt(subreddit_clause)
        min_dt = RedditMemeRepo.min_dt(subreddit_clause)
        max_percentile_dt = RedditMemeRepo.max_dt(and_(subreddit_clause, RedditMemes.percentile != None)) or min_dt
        if not max_percentile_dt or not max_dt or not min_dt or max_dt-min_dt < timedelta(days=rank_over_days):
            return
        start_arrow = arrow.get(max_percentile_dt).floor("hour")
        end_arrow = arrow.utcnow().floor("hour").shift(days=-1, seconds=-1)
        clause = and_(subreddit_clause, RedditMemes.created_at > start_arrow.datetime)
        with site_session_maker() as session:
            reddit_id_to_meme: dict[str, RedditMemes] = {meme.reddit_id: meme for meme in session.execute(select(RedditMemes).where(clause)).scalars()}
            df = pd.DataFrame.from_records([{"reddit_id": meme.reddit_id,
                                             "upvotes": meme.upvotes,
                                             "created_at": meme.created_at,
                                             "percentile": meme.percentile} for meme in reddit_id_to_meme.values()])
            while start_arrow.shift(days=rank_over_days) < end_arrow:
                create_at_col = df["created_at"].astype(np.int64).divide(1_000_000_000)
                mask_start_ranking = create_at_col.gt(start_arrow.timestamp())
                mask_end_ranking = create_at_col.lt(start_arrow.shift(days=rank_over_days).timestamp())
                frame = df.loc[mask_start_ranking & mask_end_ranking, ["upvotes", "reddit_id", "percentile"]]
                frame["percentile"] = frame["upvotes"].rank(pct=True)
                mask_end_window = create_at_col.lt(start_arrow.shift(days=rank_over_days//2+1).timestamp())
                for _, row in frame.loc[mask_end_window].iterrows():
                    meme = reddit_id_to_meme[row["reddit_id"]]
                    if not meme.percentile:
                        meme.percentile = row["percentile"]
                session.commit()
                start_arrow = start_arrow.shift(days=1)

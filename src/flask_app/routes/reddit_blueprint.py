

import random
from dataclasses import dataclass, field

from apiflask import APIBlueprint
from marshmallow_dataclass import class_schema
from praw.reddit import Submission

from src.modules.reddit_meme.reddit_scraper import reddit_objs

reddit_blueprint = APIBlueprint('reddit_blueprint', __name__, url_prefix="/reddit")


@dataclass
class SubmissionIn:
    id: str = field(metadata={'required': True})


@dataclass
class SubmissionOut:
    upvote_ratio: float
    upvotes: int
    downvotes: int


@reddit_blueprint.post("/vote_data")
@reddit_blueprint.input(class_schema(SubmissionIn)(), location='json')
@reddit_blueprint.output(class_schema(SubmissionOut)())
def vote_data(submission_in: SubmissionIn):
    submission: Submission = random.choice(reddit_objs).submission(id=submission_in.id)
    return {"upvote_ratio": submission.upvote_ratio,
            "upvotes": submission.score,
            "downvotes": round(submission.score / submission.upvote_ratio) - submission.score}

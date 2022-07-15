import time
from dataclasses import dataclass, field
from typing import Any

import arrow
from IPython.core.display import clear_output
from sqlalchemy import func, select
from src.lib import logger, utils
from src.lib.services.database import site_session_maker
from src.lib.versioning import Versioner
from src.modules.ai.ai_model_service import AiModelService
from src.modules.ai.model_runner.model_runner_dataset import (
    Entity, ImageError, MemeClfPreditingDataset)
from src.modules.generated.site_tables import TemplatePredictions


@dataclass
class Timer:
    exec_start: int = field(default_factory=lambda: int(time.time()))
    round_start: int = field(default_factory=lambda: int(time.time()))
    uptime: int = 0

    def display(self):
        round_time = int(time.time() - self.round_start)
        self.round_start = int(time.time())
        self.uptime = int(time.time() - self.exec_start)
        utils.pretty_print(round_time=utils.secondsToText(round_time),
                           uptime=utils.secondsToText(self.uptime))


@dataclass
class ModelRunner:

    entity: Entity
    lts: bool = True
    is_celery: bool = False

    def __post_init__(self):
        self.version = Versioner.meme_clf(lts=self.lts)
        self.dataset = MemeClfPreditingDataset(self.entity, self.is_celery, self.version)

    def get_error_count(self, image_error: ImageError):
        with site_session_maker() as session:
            return session.scalar(select(func.count(self.dataset.meme_entity.id)).filter_by(image_error=image_error.value))

    def display_errors(self):
        utils.display_dict_as_df({image_error.value: self.get_error_count(image_error) for image_error in ImageError})

    def execute(self, print_every: int):
        if not self.is_celery:
            self.timer = Timer()
        self.num_to_do = self.dataset.count()
        logger.info("num_to_do: %s", self.num_to_do)
        for self.iteration, (images, ids) in enumerate(MemeClfPreditingDataset.data_loader(self.entity, self.is_celery, self.version), start=1):
            names = AiModelService.meme_clf(images)
            results: list[Any] = [
                TemplatePredictions(not_meme=name == "not_meme",
                                    not_template=name == "not_template",
                                    template_name=name if name not in ["not_meme", "not_template"] else None,
                                    version=self.version,
                                    meme_id=id if self.entity is Entity.Meme else None,
                                    reddit_meme_id=id if self.entity is Entity.RedditMeme else None) for id, name in zip(ids, names)
            ]
            with site_session_maker() as session:
                session.add_all(results)
                session.commit()
            if not self.is_celery and self.iteration % print_every == 0:
                self.print_stats()
            else:
                logger.info("iteration: %s num_ids: %s", self.iteration, len(ids))

    def print_stats(self):
        clear_output()
        num_done = self.iteration * 128
        self.timer.display()
        total_memes = self.dataset.total_memes()
        with site_session_maker() as session:
            unofficial_memes_done = session.scalar(select(func.count(TemplatePredictions.id)).filter_by(version=self.version))
            unofficial_memes_found = session.scalar(select(func.count(TemplatePredictions.id))
                                                    .where(TemplatePredictions.template_name.is_not(None))
                                                    .filter_by(version=self.version))
        assert unofficial_memes_done and unofficial_memes_found
        num_left = total_memes-unofficial_memes_done
        utils.display_as_df(iteration=self.iteration,
                            timestamp=arrow.utcnow().to("local").format("HH:mm:ss"),
                            num_to_do=self.num_to_do,
                            num_done=num_done,
                            eta=utils.secondsToText((self.timer.uptime * num_left) // num_done),
                            total_memes=total_memes,
                            unofficial_memes_done=unofficial_memes_done,
                            unofficial_memes_found=unofficial_memes_found,
                            find_ratio=round(unofficial_memes_found / unofficial_memes_done, 3),
                            done_ratio=round(unofficial_memes_done / total_memes, 3))
        self.display_errors()

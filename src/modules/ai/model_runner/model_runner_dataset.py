from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from multiprocessing import cpu_count
from typing import Any, ClassVar, Iterable, Optional, Tuple

import arrow
from PIL import UnidentifiedImageError
from sqlalchemy import case, func, select
from sqlalchemy.sql.expression import ClauseElement
from src.lib.errors import Errors
from src.lib.image_url import ImageUrlUtils
from src.services.database import site_session_maker
from src.modules.versioning import Versioner
from src.modules.ai.transforms import Transformations
from src.modules.generated.site_tables import (Memes, RedditMemes,
                                               TemplatePredictions)
from torch import Tensor
from torch.utils.data import DataLoader, get_worker_info
from torch.utils.data.dataset import IterableDataset


class Entity(Enum):
    Meme = "memes"
    RedditMeme = "reddit_memes"


class ImageError(Enum):
    IsDeleted = "IsDeleted"
    Malformed = "Malformed"
    NoImage = "NoImage"
    Connection = "Connection"
    Unidentified = "Unidentified"
    Unknown = "Unknown"

    @classmethod
    def exception_to_enum(cls, e: Exception):
        if e is Errors.IsDeleted:
            return ImageError.IsDeleted
        elif e is Errors.MalformedImage:
            return ImageError.Malformed
        elif e is Errors.NoImage:
            return ImageError.NoImage
        elif e is ConnectionError:
            return ImageError.Connection
        elif e is UnidentifiedImageError:
            return ImageError.Unidentified
        else:
            return ImageError.Unknown


@dataclass
class MemeClfPreditingDataset(IterableDataset[Tensor]):
    celery_grace_period: ClassVar[timedelta] = timedelta(days=4)

    entity_enum: Entity
    is_celery: bool
    version: str

    def __post_init__(self):
        if self.entity_enum is Entity.Meme:
            self.meme_entity = Memes
        elif self.entity_enum is Entity.RedditMeme:
            self.meme_entity = RedditMemes

    def _base_query(self, selects: Optional[ClauseElement] = None):
        selectable = self.meme_entity if selects is None else selects
        q = (select(selectable)
             .where(self.meme_entity.image_error.is_(None))
             .outerjoin(TemplatePredictions)
             .group_by(self.meme_entity.id)
             .having(func.count(case((TemplatePredictions.version == self.version, 1))) == 0))
        if self.is_celery:
            grace_period = arrow.utcnow().replace(minute=0, second=0).shift(days=-self.celery_grace_period.days).datetime
            q = q.where(self.meme_entity.created_at >= grace_period)
        if self.meme_entity is RedditMemes:
            return q.group_by(TemplatePredictions.reddit_meme_id)
        else:
            return q.group_by(TemplatePredictions.meme_id)

    def _get_workers_query(self):
        worker_info: Any = get_worker_info()
        if not worker_info or (num_workers := worker_info.num_workers) < 2:
            return self._base_query()
        else:
            return self._base_query().where((self.meme_entity.idx % num_workers) == worker_info.id)

    def __iter__(self):
        with site_session_maker() as session:
            for meme in session.scalars(self._get_workers_query()):
                try:
                    yield (Transformations.toVGG16Input(ImageUrlUtils.get_image(meme.url, check_is_deleted=True)), meme.id)
                except Exception as e:
                    meme.image_error = ImageError.exception_to_enum(e).value
                    session.add(meme)
                    session.commit()

    def count(self) -> int:
        with site_session_maker() as session:
            q = self._base_query(func.count(self.meme_entity.id))
            return session.scalar(q)

    def total_memes(self) -> int:
        with site_session_maker() as session:
            q = select(func.count(self.meme_entity.id)).where(self.meme_entity.image_error.is_(None))
            return session.scalar(q)

    @classmethod
    def data_loader(cls, entity_enum: Entity, is_celery: bool, meme_version: str, num_workers: Optional[int] = None) -> Iterable[Tuple[Tensor, list[str]]]:
        dataset = cls(entity_enum, is_celery, meme_version)
        if not num_workers:
            num_workers = 0 if is_celery else cpu_count()
        return DataLoader(dataset, batch_size=128, num_workers=num_workers)

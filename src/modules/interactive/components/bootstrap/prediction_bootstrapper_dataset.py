from dataclasses import dataclass
from multiprocessing import cpu_count
from typing import Any, Generator, Iterable, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.sql.expression import case
from src.lib import logger
from src.lib.image_url import ImageUrlUtils
from src.lib.services.database import (site_session_maker,
                                       training_session_maker)
from src.modules.ai.transforms import Transformations
from src.modules.generated.site_tables import RedditMemes
from src.modules.training_database.training_database_entities import \
    ValidationEntity
from torch import Tensor
from torch.utils.data import DataLoader, get_worker_info
from torch.utils.data.dataset import IterableDataset


@dataclass
class PredictionBootstrapperDataset(IterableDataset[tuple[str, str, Tensor]]):
    version: str

    def __post_init__(self):
        self.meme_val_id_dict = self._get_meme_val_id_dict()

    def _get_meme_val_id_dict(self) -> dict[str, str]:
        clause = or_(ValidationEntity.correct.is_(True),
                     ValidationEntity.not_meme.is_(True),
                     ValidationEntity.not_template.is_(True))
        with training_session_maker() as session:
            reddit_meme_ids = session.scalars(select(ValidationEntity.reddit_meme_id)
                                              .filter(clause)
                                              .group_by(ValidationEntity.reddit_meme_id)
                                              .having(func.count(case((ValidationEntity.version == self.version, 1))) == 0))
            assert reddit_meme_ids
            q = select(ValidationEntity.id, ValidationEntity.reddit_meme_id).filter(ValidationEntity.reddit_meme_id.in_(reddit_meme_ids))
            return {meme_id: val_id for val_id, meme_id in session.execute(q)}

    def _get_meme_val_ids_url(self) -> Generator[tuple[str, str, str], None, None]:
        worker_info: Any = get_worker_info()
        if not worker_info or (num_workers := worker_info.num_workers) < 2:
            dicty = self.meme_val_id_dict
        else:
            correct_validations = self.meme_val_id_dict
            chunk_size = len(correct_validations) // num_workers
            dicty = dict(list(correct_validations.items())[worker_info.id * chunk_size:(worker_info.id + 1) * chunk_size])
        with site_session_maker() as session:
            for meme_id, url in session.execute(select(RedditMemes.id, RedditMemes.url).filter(RedditMemes.id.in_(list(dicty.keys())))):
                yield meme_id, dicty[meme_id], url

    def __iter__(self):
        for meme_id, val_id, url in self._get_meme_val_ids_url():
            try:
                yield (meme_id, val_id, url, Transformations.toVGG16Input(ImageUrlUtils.get_image(url, check_is_deleted=True)))
            except:
                logger.info("failed")

    def count(self) -> int:
        return len(self.meme_val_id_dict)

    @classmethod
    def data_loader(cls, meme_version: str) -> tuple[int, Iterable[Tuple[list[str], Tensor, list[str], Tensor]]]:
        dataset = cls(meme_version)
        return dataset.count(), DataLoader(dataset, batch_size=128, num_workers=cpu_count())

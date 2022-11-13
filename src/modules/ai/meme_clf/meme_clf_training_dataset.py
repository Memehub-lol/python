import random
from dataclasses import dataclass
from enum import Enum
from itertools import repeat
from typing import ClassVar, Iterable, TypeVar, cast

import torch
from PIL import Image as Img
from sqlalchemy import func, select
from sqlalchemy.orm.session import Session
from src.modules.ai.static_data import StaticData
from src.modules.ai.transforms import Transformations
from src.modules.training_database.training_database_entities import (
    NotMemeEntity, NotTemplateEntity, TemplateEntity)
from src.services.database import training_session_maker
from torch import Tensor
from torch.utils.data.dataloader import DataLoader
from torch.utils.data.dataset import IterableDataset

T = TypeVar("T")


class ELoadSet(Enum):
    TRAINING = "training"
    TRANSFORMS_EVAL = "transforms_eval"
    VALIDATION_EVAL = "validation_eval"

    def is_training(self):
        return self is ELoadSet.TRAINING

    def use_test_set(self):
        return self in [ELoadSet.TRANSFORMS_EVAL, ELoadSet.VALIDATION_EVAL]

    def use_transforms(self):
        return self.is_training() or self is ELoadSet.TRANSFORMS_EVAL


def _fill_list(listy: list[T], num: int) -> list[T]:
    if listy and len(listy) < num:
        listy = listy * (num // len(listy)+1)
        listy = listy[:num]
    return listy


@dataclass
class MemeClfTrainingDataset(IterableDataset[tuple[Tensor, Tensor]]):
    transform_prob: ClassVar[float] = 0.75

    meme_version: str
    load_set: ELoadSet
    batch_size: int = 128

    def __post_init__(self):
        super(MemeClfTrainingDataset).__init__()
        self.static_data = StaticData.load(meme_version=self.meme_version)
        self.is_training = self.load_set.is_training()
        self.num_workers = 5 if self.is_training else 1
        self.num_each_template = 64 if self.is_training else 5
        self.num_names = len(self.static_data.get_template_names())
        not_meme_portion = 0.15 if self.is_training else 0.1
        self.num_not_meme = int(self.num_each_template * self.num_names * not_meme_portion)
        not_template_portion = 0.35 if self.is_training else 0.1
        self.num_not_template = int(self.num_each_template * self.num_names * not_template_portion)
        self.use_transforms = self.load_set.use_transforms()
        self.transforms = Transformations.get_transforms()

    def __len__(self):
        images_per_worker = (self.num_not_template +
                             self.num_not_meme +
                             self.num_each_template * self.num_names)
        return self.num_workers * (images_per_worker) // self.batch_size

    def _get_not_meme_paths(self, session: Session):
        query = (select(NotMemeEntity.path)
                 .order_by(func.random())
                 .filter_by(is_test_set=not self.is_training)
                 .limit(self.num_not_meme))
        list_gen = zip(cast(list[str], session.scalars(query)), repeat("not_meme"))
        return _fill_list(list(list_gen), self.num_not_meme)

    def _get_not_template_paths(self, session: Session):
        query = (select(NotTemplateEntity.path)
                 .order_by(func.random())
                 .filter_by(is_test_set=not self.is_training)
                 .limit(self.num_not_template))
        list_gen = zip(cast(list[str], session.scalars(query)), repeat("not_template"))
        return _fill_list(list(list_gen), self.num_not_template)

    def _get_template_name_paths(self, name: str, session: Session):
        query = (select(TemplateEntity.path)
                 .filter_by(name=name, is_test_set=not self.is_training)
                 .order_by(func.random())
                 .limit(self.num_each_template))
        list_gen = zip(cast(list[str], session.scalars(query)), repeat(name))
        return _fill_list(list(list_gen), self.num_each_template)

    def _get_template_paths(self, session: Session):
        path_names: list[tuple[str, str]] = []
        for name in self.static_data.get_template_names():
            assert (template_path_names := self._get_template_name_paths(name, session))
            path_names.extend(template_path_names)
        return path_names

    def _get_path_names(self):
        with training_session_maker() as session:
            path_names = (self._get_not_meme_paths(session) +
                          self._get_not_template_paths(session) +
                          self._get_template_paths(session))
        if self.is_training:
            random.shuffle(path_names)
        return path_names

    def __iter__(self):
        for path, name in self._get_path_names():
            use_tensor_only = name == "not_meme" or not self.use_transforms or torch.randn(1).item() > self.transform_prob
            transformer = Transformations.toTensorOnly if use_tensor_only else self.transforms
            yield transformer(Img.open(path)), self.static_data.get_num(name)

    def _get_dl_kwargs(self):
        return {"batch_size": self.batch_size, "num_workers": self.num_workers}

    @classmethod
    def data_loader(cls,
                    meme_version: str,
                    load_set: ELoadSet,
                    persistent_workers: bool,
                    drop_last: bool = True) -> tuple[int, Iterable[tuple[Tensor, Tensor]]]:
        dataset = cls(meme_version=meme_version, load_set=load_set)
        return len(dataset), DataLoader(dataset,
                                        drop_last=drop_last,
                                        persistent_workers=persistent_workers,
                                        **dataset._get_dl_kwargs())

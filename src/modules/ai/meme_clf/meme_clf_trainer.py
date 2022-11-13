from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, TypedDict, cast

import torch
import torch.nn as nn
import wandb
from src.enums.e_memeclf_version import EMemeClfVersion
from src.modules.ai.meme_clf.lib.meme_clf_timer import Timer
from src.modules.ai.meme_clf.meme_clf_net import MemeClf, MemeClfLayer
from src.modules.ai.meme_clf.meme_clf_training_dataset import (
    ELoadSet, MemeClfTrainingDataset)
from src.modules.ai.static_data import StaticData
from src.services.environment import Environment
from torch import nn
from torch.optim import SGD
from tqdm import tqdm


@dataclass
class Settings:
    target_acc_dense: float = 0.95
    target_acc_all_layers: float = 0.95

    def get_target_acc(self, dense_only: bool):
        return self.target_acc_dense if dense_only else self.target_acc_all_layers


@dataclass
class MemeClfTrainer:
    fresh: bool = field(default_factory=lambda: bool(input("want fresh?")))
    lts: Optional[bool] = None
    meme_version: Optional[str] = None
    settings: Settings = field(default_factory=Settings)
    timer: Timer = field(default_factory=Timer)

    def __post_init__(self):
        self.meme_version = EMemeClfVersion.reduce_to_meme_version(lts=self.lts, meme_version=self.meme_version)
        self.static_data = StaticData.load(meme_version=self.meme_version, fresh=self.fresh)

    @contextmanager
    def _in_eval(self, layers: list[MemeClfLayer]):
        for layer in layers:
            getattr(self.model, layer.value).eval()
        yield
        for layer in layers:
            getattr(self.model, layer.value).train()

    @contextmanager
    def _dataloaders(self):
        assert self.meme_version
        dataloaders = {load_set: MemeClfTrainingDataset.data_loader(meme_version=self.meme_version,
                                                                    load_set=load_set,
                                                                    persistent_workers=True) for load_set in ELoadSet}
        yield dataloaders
        del dataloaders

    def _train_loop(self, dense_only: bool):
        UPDATE_PBAR_EVERY = 100
        self.model: MemeClf = MemeClf.load(fresh=self.fresh, meme_version=self.meme_version, sgd_kwargs=sgd_kwargs,
                                           output_size=len(self.static_data.get_all_names()))
        self.features_opt = SGD(self.model.features.parameters(), **wandb.config.sgd_kwargs)
        self.dense_opt = SGD(self.model.dense.parameters(), **wandb.config.sgd_kwargs)
        self.criterion: Callable[..., torch.Tensor] = nn.CrossEntropyLoss()
        with cast(Any, wandb.init(project="meme-clf-project", job_type="training", config=self.config)), self._dataloaders() as self.dataloaders:
            _ = wandb.watch(self.model, self.criterion, log="all", log_freq=10)
            ESTIMATED_INTERATIONS, dataloader = self.dataloaders[ELoadSet.TRAINING]
            max_val_acc = 0
            while max_val_acc < self.settings.get_target_acc(dense_only=dense_only):
                with self.timer.is_training(), tqdm(total=ESTIMATED_INTERATIONS) as pbar:
                    for idx, (inputs, labels) in enumerate(dataloader, 1):
                        loss = self.train_step(inputs.to(Environment.PYTORCH_DEVICE), labels.to(Environment.PYTORCH_DEVICE), dense_only=dense_only)
                        wandb.log({"loss": loss}, step=1)
                        if idx % UPDATE_PBAR_EVERY == 0:
                            _ = pbar.update(UPDATE_PBAR_EVERY)
                with self._in_eval(MemeClfLayer.get_layers(dense_only)):
                    transforms_correct, transforms_total = self._get_eval_correct_total(ELoadSet.TRANSFORMS_EVAL)
                    validation_correct, validation_total = self._get_eval_correct_total(ELoadSet.VALIDATION_EVAL)
                    wandb.log(dict(transforms_correct=transforms_correct,
                                   transforms_total=transforms_total,
                                   transforms_acc=transforms_correct/transforms_total,
                                   validation_correct=validation_correct,
                                   validation_total=validation_total,
                                   validation_acc=validation_correct/validation_total), step=1)
                    if validation_correct/validation_total > max_val_acc:
                        self.model.save()

    def train_dense(self):
        with self._in_eval([MemeClfLayer.FEATURES]):
            self._train_loop(dense_only=True)

    def train_full(self):
        self._train_loop(dense_only=False)

    @torch.no_grad()
    def _predict(self, image: torch.Tensor) -> str:
        return self.static_data.get_name(int(self.model.forward(image.to(Environment.PYTORCH_DEVICE).unsqueeze(0)).cpu().detach().item()))

    @torch.no_grad()
    def _get_eval_correct_total(self, load_set: ELoadSet):
        correct, total = 0, 0
        for (inputs, labels) in self.dataloaders[load_set][1]:
            pred = self.model.forward(inputs.to(Environment.PYTORCH_DEVICE))
            correct += int(torch.sum(pred == labels.to(Environment.PYTORCH_DEVICE)).cpu().detach().item())
            total += len(labels)
        return correct, total

    def dense_train_step(self, batch: torch.Tensor, labels: torch.Tensor) -> float:
        with torch.no_grad():
            features = self.features(batch)
        self.dense_opt.zero_grad()
        loss = self.loss(self.dense(features), labels)
        _ = loss.backward(torch.ones_like(loss))
        _ = self.dense_opt.step()
        return loss.detach().cpu().item()

    def train_step(self, batch: torch.Tensor, labels: torch.Tensor, dense_only: bool):
        if dense_only:
            return self.dense_train_step(batch, labels)
        return self.full_train_step(batch, labels)

    def full_train_step(self, batch: torch.Tensor, labels: torch.Tensor) -> float:
        self.features_opt.zero_grad()
        self.dense_opt.zero_grad()
        loss = self.loss(self.dense(self.features(batch)), labels)
        _ = loss.backward(torch.ones_like(loss))
        _ = self.features_opt.step()
        _ = self.dense_opt.step()
        return loss.detach().cpu().item()

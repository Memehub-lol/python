from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional

import arrow
import torch
from IPython.core.display import clear_output
from src.lib import utils
from src.services.environment import Environment
from src.modules.versioning import Versioner
from src.modules.ai.meme_clf.lib.meme_clf_ephemeral import Ephemeral
from src.modules.ai.meme_clf.lib.meme_clf_eval_stats import EvalStats
from src.modules.ai.meme_clf.lib.meme_clf_timer import Timer
from src.modules.ai.meme_clf.meme_clf_net import (MemeClf, MemeClfLayer,
                                                  SGDKwargs)
from src.modules.ai.meme_clf.meme_clf_training_dataset import (
    ELoadSet, MemeClfTrainingDataset)
from src.modules.ai.meme_clf.model_stats import MemeClfModelStats
from src.modules.ai.static_data import StaticData
from tqdm import tqdm

sgd_kwargs: SGDKwargs = {"lr": 0.000_1,
                         "momentum": 0.9,
                         "dampening": 0,
                         "weight_decay": 0.000_1,
                         "nesterov": True}


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
    ephemeral: Ephemeral = field(default_factory=Ephemeral)
    settings: Settings = field(default_factory=Settings)
    timer: Timer = field(default_factory=Timer)

    def __post_init__(self):
        self.meme_version = Versioner.reduce_to_meme_version(lts=self.lts, meme_version=self.meme_version)
        self.static_data = StaticData.load(meme_version=self.meme_version, fresh=self.fresh)
        self.model_stats = MemeClfModelStats.load(fresh=self.fresh, meme_version=self.meme_version)
        self.model = MemeClf.load(fresh=self.fresh, meme_version=self.meme_version, sgd_kwargs=sgd_kwargs, output_size=len(self.static_data.get_all_names()))

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
        with self._dataloaders() as self.dataloaders:
            ESTIMATED_INTERATIONS, dataloader = self.dataloaders[ELoadSet.TRAINING]
            while self.model_stats.max_val_acc < self.settings.get_target_acc(dense_only=dense_only):
                with self.timer.is_training(), tqdm(total=ESTIMATED_INTERATIONS) as pbar:
                    for idx, (inputs, labels) in enumerate(dataloader, 1):
                        loss = self.model.train_step(inputs.to(Environment.PYTORCH_DEVICE), labels.to(Environment.PYTORCH_DEVICE), dense_only=dense_only)
                        self.ephemeral.losses.append(loss)
                        if idx % UPDATE_PBAR_EVERY == 0:
                            pbar.update(UPDATE_PBAR_EVERY)
                with self._in_eval(MemeClfLayer.get_layers(dense_only)):
                    self._update_stats()
                self.display_stats()

    def train_dense(self):
        with self._in_eval([MemeClfLayer.FEATURES]):
            self._train_loop(dense_only=True)

    def train_full(self):
        self._train_loop(dense_only=False)

    def _humanize_pred(self, pred: int) -> str:
        return self.static_data.get_name(pred)

    @torch.no_grad()
    def _predict(self, image: torch.Tensor) -> str:
        return self._humanize_pred(int(self.model.forward(image.to(Environment.PYTORCH_DEVICE).unsqueeze(0)).cpu().detach().item()))

    @torch.no_grad()
    def _get_eval_stats(self, load_set: ELoadSet):
        correct, total = 0, 0
        for (inputs, labels) in self.dataloaders[load_set][1]:
            pred = self.model.forward(inputs.to(Environment.PYTORCH_DEVICE))
            correct += int(torch.sum(pred == labels.to(Environment.PYTORCH_DEVICE)).cpu().detach().item())
            total += len(labels)
        return EvalStats(correct=correct, total=total, acc=correct/total)

    def _update_stats(self) -> None:
        self.ephemeral.update(transforms=self._get_eval_stats(ELoadSet.TRANSFORMS_EVAL),
                              validation=self._get_eval_stats(ELoadSet.VALIDATION_EVAL))
        is_new_max = self.model_stats.update(self.ephemeral)
        self.model_stats.update_total_time(self.timer.round_start)
        self.timer.new_round()
        if is_new_max:
            self.model.save()
            self.model_stats.save()

    def display_stats(self) -> None:
        clear_output()
        utils.display_dicts_as_dfs([dict(val_correct=f"{self.ephemeral.validation.correct}/{self.ephemeral.validation.total}",
                                         val_acc=round(self.model_stats.val_acc_history[-1], 3),
                                         max_val_acc=round(self.model_stats.max_val_acc, 3),
                                    trans_correct=f"{self.ephemeral.transforms.correct}/{self.ephemeral.transforms.total}",
                                         trans_acc=round(self.model_stats.trans_acc_history[-1], 3),
                                         max_trans_acc=round(self.model_stats.max_trans_acc, 3)),
                                    dict(name=self.model.name,
                                         iteration=self.model_stats.iteration,
                                         loss=round(self.ephemeral.new_loss, 3),
                                         min_loss=round(self.model_stats.min_loss, 3),
                                         timestamp=arrow.utcnow().to("local").format("HH:mm:ss"),
                                         train_runtime=utils.secondsToText(self.timer.train_runtime),
                                         round_runtime=utils.secondsToText(self.timer.round_runtime),
                                         uptime=utils.secondsToText(self.timer.uptime),
                                         total_time=utils.secondsToText(self.model_stats.total_time),
                                         eta=utils.secondsToText(self.model_stats.get_eta()))])
        self.model_stats.print_graphs()

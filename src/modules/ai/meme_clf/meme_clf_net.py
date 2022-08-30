from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Any, Callable, ClassVar, Optional, TypedDict, cast

import torch
import torch.nn as nn
from src.lib import decorators
from src.services.environment import Environment
from src.modules.versioning import Versioner
from src.modules.ai.meme_clf.lib.meme_clf_path import ESaveFolder, MemeClfPath
from torch import nn
from torch._C import ScriptModule
from torch.jit._script import script
from torch.jit._serialization import save
from torch.optim import SGD
from torchvision.models import vgg16


class SGDKwargs(TypedDict, total=False):
    lr: float
    momentum: float
    dampening: float
    weight_decay: float
    nesterov: bool


class MemeClfLayer(Enum):
    DENSE = "dense"
    FEATURES = "features"

    @staticmethod
    def get_layers(dense_only: bool):
        if dense_only:
            return [MemeClfLayer.DENSE]
        return [MemeClfLayer.FEATURES, MemeClfLayer.FEATURES]


class MemeClfKwargsDict(TypedDict):
    meme_version: str
    output_size: int
    sgd_kwargs: SGDKwargs


class MemeClf(nn.Module):
    name: ClassVar[str] = "meme_clf"

    def __init__(self, output_size: int, meme_version: str, sgd_kwargs: SGDKwargs):
        super(MemeClf, self).__init__()
        self.kwargs: MemeClfKwargsDict = {"meme_version": meme_version, "output_size": output_size, "sgd_kwargs": sgd_kwargs}
        self.features = nn.Sequential(*(list(vgg16(pretrained=True).children())[:-1]))
        self.dense = nn.Sequential(nn.Flatten(),
                                   nn.Linear(25088, 4096),
                                   nn.Dropout(0.5, True),
                                   nn.ReLU(True),
                                   nn.Linear(4096, 4096),
                                   nn.Dropout(0.5, True),
                                   nn.ReLU(True),
                                   nn.Linear(4096, output_size))
        self.features_opt = SGD(self.features.parameters(), **sgd_kwargs)
        self.dense_opt = SGD(self.dense.parameters(), **sgd_kwargs)
        self.loss: Callable[..., torch.Tensor] = nn.CrossEntropyLoss()

    def get_features_lr(self) -> float:
        param_groups = cast(list[dict[str, Any]], self.features_opt.param_groups)
        return param_groups[0]["lr"]

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

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return torch.argmax(self.dense(self.features(images)), dim=1)

    @contextmanager
    def _model_on_cpu(self):
        _ = self.to(torch.device("cpu"))
        yield
        _ = self.to(Environment.PYTORCH_DEVICE)

    @classmethod
    def _get_path(cls, folder: ESaveFolder, name: str, meme_version: str, backup: bool):
        return MemeClfPath.build_path_by_version(e_save_folder=folder,
                                                 meme_version=meme_version,
                                                 backup=backup) + f"/{name}.pt"

    @classmethod
    @decorators.on_error_use_backup()
    def load_features_model(cls, meme_version: str, backup: bool = False):
        path = cls._get_path(ESaveFolder.REG, "features", meme_version=meme_version, backup=backup)
        return cast(nn.Module, torch.load(path)).to(Environment.PYTORCH_DEVICE)

    @decorators.do_backup_also()
    def save(self, backup: bool = False) -> None:
        meme_version: str = self.kwargs["meme_version"]
        for path in [reg_full := self._get_path(ESaveFolder.REG, name=self.name, backup=backup, meme_version=meme_version),
                     reg_features := self._get_path(ESaveFolder.REG, name="features", backup=backup, meme_version=meme_version),
                     reg_dense := self._get_path(ESaveFolder.REG, name="dense", backup=backup, meme_version=meme_version),
                     jit_cpu_features := self._get_path(ESaveFolder.JIT_CPU, name="features", backup=backup, meme_version=meme_version),
                     jit_cpu_dense := self._get_path(ESaveFolder.JIT_CPU, name="dense", backup=backup, meme_version=meme_version),
                     jit_gpu_features := self._get_path(ESaveFolder.JIT_GPU, name="features", backup=backup, meme_version=meme_version),
                     jit_gpu_dense := self._get_path(ESaveFolder.JIT_GPU, name="dense", backup=backup, meme_version=meme_version)]:
            Path(path).parent.mkdir(exist_ok=True, parents=True)
        with self._model_on_cpu():
            torch.save([self.kwargs, self.state_dict()], reg_full)
            torch.save(self.features, reg_features)
            torch.save(self.dense, reg_dense)
            save(cast(ScriptModule, script(self.features)), jit_cpu_features)
            save(cast(ScriptModule, script(self.dense)), jit_cpu_dense)
        save(cast(ScriptModule, script(self.features)), jit_gpu_features)
        save(cast(ScriptModule, script(self.dense)), jit_gpu_dense)

    @classmethod
    @decorators.on_error_use_backup()
    def _load_from_disk_by_version(cls, meme_version: str, backup: bool):
        path = cls._get_path(ESaveFolder.REG, name=cls.name, meme_version=meme_version, backup=backup)
        kwargs, state = cast(tuple[Any, Any], torch.load(path))
        model = MemeClf(**kwargs)
        _ = model.load_state_dict(state)
        return model.to(Environment.PYTORCH_DEVICE)

    @classmethod
    def load(cls, fresh: bool, sgd_kwargs: SGDKwargs, output_size: int, meme_version: Optional[str] = None, lts: Optional[bool] = None):
        meme_version = Versioner.reduce_to_meme_version(meme_version, lts)
        if fresh:
            assert sgd_kwargs, output_size
            return cls(sgd_kwargs=sgd_kwargs, output_size=output_size, meme_version=meme_version).to(Environment.PYTORCH_DEVICE)
        return cls._load_from_disk_by_version(meme_version=meme_version, backup=False)

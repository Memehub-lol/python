from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import ClassVar, TypedDict, cast

import torch
import torch.nn as nn
from src.enums.e_memeclf_path import EMemeClfPath
from src.lib import decorators
from src.services.environment import Environment
from torch import nn
from torch._C import ScriptModule
from torchvision.models import vgg16


class MemeClfLayer(Enum):
    DENSE = "dense"
    FEATURES = "features"

    @staticmethod
    def get_layers(dense_only: bool):
        if dense_only:
            return [MemeClfLayer.DENSE]
        return [MemeClfLayer.FEATURES, MemeClfLayer.FEATURES]


class MemeClf(nn.Module):
    name: ClassVar[str] = "meme_clf"

    def __init__(self, output_size: int, meme_version: str):
        super(MemeClf, self).__init__()
        self.features = nn.Sequential(*(list(vgg16(pretrained=True).children())[:-1]))
        self.dense = nn.Sequential(nn.Flatten(),
                                   nn.Linear(25088, 4096),
                                   nn.Dropout(0.5, True),
                                   nn.ReLU(True),
                                   nn.Linear(4096, 4096),
                                   nn.Dropout(0.5, True),
                                   nn.ReLU(True),
                                   nn.Linear(4096, output_size))

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return torch.argmax(self.dense(self.features(images)), dim=1)

    @contextmanager
    def _model_on_cpu(self):
        _ = self.to(torch.device("cpu"))
        yield
        _ = self.to(Environment.PYTORCH_DEVICE)

    @classmethod
    def _get_path(cls, folder: EMemeClfPath, name: str, meme_version: str, backup: bool):
        return f"{folder.build_path_by_version(meme_version=meme_version,backup=backup)}/{name}.pt"

    @classmethod
    @decorators.on_error_use_backup()
    def load_features_model(cls, meme_version: str, backup: bool = False):
        path = cls._get_path(EMemeClfPath.REG, "features", meme_version=meme_version, backup=backup)
        return cast(nn.Module, torch.load(path)).to(Environment.PYTORCH_DEVICE)

    @decorators.do_backup_also()
    def save(self, backup: bool = False) -> None:
        meme_version: str = self.kwargs["meme_version"]
        for path in [reg_full := self._get_path(EMemeClfPath.REG, name=self.name, backup=backup, meme_version=meme_version),
                     reg_features := self._get_path(EMemeClfPath.REG, name="features", backup=backup, meme_version=meme_version),
                     reg_dense := self._get_path(EMemeClfPath.REG, name="dense", backup=backup, meme_version=meme_version),
                     jit_cpu_features := self._get_path(EMemeClfPath.JIT_CPU, name="features", backup=backup, meme_version=meme_version),
                     jit_cpu_dense := self._get_path(EMemeClfPath.JIT_CPU, name="dense", backup=backup, meme_version=meme_version),
                     jit_gpu_features := self._get_path(EMemeClfPath.JIT_GPU, name="features", backup=backup, meme_version=meme_version),
                     jit_gpu_dense := self._get_path(EMemeClfPath.JIT_GPU, name="dense", backup=backup, meme_version=meme_version)]:
            Path(path).parent.mkdir(exist_ok=True, parents=True)
        with self._model_on_cpu():
            torch.save([self.kwargs, self.state_dict()], reg_full)
            torch.save(self.features, reg_features)
            torch.save(self.dense, reg_dense)
            save(cast(ScriptModule, script(self.features)), jit_cpu_features)
            save(cast(ScriptModule, script(self.dense)), jit_cpu_dense)
        save(cast(ScriptModule, script(self.features)), jit_gpu_features)
        save(cast(ScriptModule, script(self.dense)), jit_gpu_dense)

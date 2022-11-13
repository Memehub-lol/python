import time
from dataclasses import dataclass, field
from typing import ClassVar, cast

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from src.enums.e_memeclf_path import EMemeClfPath
from src.lib.json_save_load_base import CheckpointBase
from src.modules.ai.meme_clf.lib.meme_clf_ephemeral import Ephemeral


@dataclass
class MemeClfModelStats(CheckpointBase):
    file_name: ClassVar[str] = "model_stats.json"

    iteration: int = 0
    total_time: int = 0
    max_trans_acc: float = 0
    max_val_acc: float = 0
    min_loss: float = np.inf
    loss_history: list[float] = field(default_factory=list)
    trans_acc_history: list[float] = field(default_factory=list)
    val_acc_history: list[float] = field(default_factory=list)

    def update(self, ephemeral: Ephemeral):
        self.iteration += 1
        self.min_loss = min(ephemeral.new_loss, self.min_loss)
        self.loss_history.append(ephemeral.new_loss)
        self.max_trans_acc = max(ephemeral.transforms.acc, self.max_trans_acc)
        is_new_max = ephemeral.validation.acc > self.max_val_acc
        self.max_val_acc = max(ephemeral.validation.acc, self.max_val_acc)
        self.trans_acc_history.append(ephemeral.transforms.acc)
        self.val_acc_history.append(ephemeral.validation.acc)
        return is_new_max

    def update_total_time(self, round_start: int):
        self.total_time += int(time.time() - round_start)

    def get_eta(self):
        return int(self.total_time * (1 - self.max_val_acc) / self.max_val_acc)

    @classmethod
    def _get_path(cls, meme_version: str, backup: bool):
        return EMemeClfPath.path_by_version(meme_version, backup=backup)

    def print_graphs(self):
        plt.style.use('dark_background')
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(16, 4))
        fig.tight_layout()
        axes = cast(list[Axes], axes)
        _ = axes[0].plot(range(len(self.loss_history)), self.loss_history)
        _ = axes[0].grid()
        axes[0].set_title("Loss Full")
        _ = axes[1].plot(range(len(self.val_acc_history)), self.val_acc_history, '-g')
        _ = axes[1].plot(range(len(self.trans_acc_history)), self.trans_acc_history, '-r')
        _ = axes[1].legend(['validation', 'validation transforms'])
        _ = axes[1].grid()
        axes[1].set_title("Accuracies")
        plt.show()

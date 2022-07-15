from dataclasses import dataclass, field

import numpy as np
from src.modules.ai.meme_clf.lib.meme_clf_eval_stats import EvalStats


@dataclass
class Ephemeral:
    epoch: int = 0
    transforms: EvalStats = field(default_factory=EvalStats)
    validation: EvalStats = field(default_factory=EvalStats)

    new_loss: float = 0
    losses: list[float] = field(default_factory=list)

    def update(self, transforms: EvalStats, validation: EvalStats):
        self.transforms = transforms
        self.validation = validation
        self.new_loss: float = np.mean(self.losses)
        self.losses = []

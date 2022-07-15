from dataclasses import dataclass


@dataclass
class EvalStats:
    correct: int = 0
    total: int = 0
    acc: float = 0

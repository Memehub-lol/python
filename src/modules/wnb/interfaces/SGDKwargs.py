from typing import TypedDict


class SGDKwargs(TypedDict, total=False):
    lr: float
    momentum: float
    dampening: float
    weight_decay: float
    nesterov: bool

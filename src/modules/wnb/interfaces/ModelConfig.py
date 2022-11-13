from typing import TypedDict

from src.modules.wnb.interfaces.SGDKwargs import SGDKwargs


class ModelConfig(TypedDict):
    output_size: int
    sgd_kwargs: SGDKwargs

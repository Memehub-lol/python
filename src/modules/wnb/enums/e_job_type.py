from enum import Enum


class EJobType(Enum):
    Dataset = "dataset"
    Train = "train"
    Eval = "eval"

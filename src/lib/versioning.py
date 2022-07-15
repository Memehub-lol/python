import os
from enum import Enum
from typing import ClassVar, Optional


class EMemeClfVersion(Enum):
    LTS = "0.0.7"
    EDGE = "0.0.8"


class Versioner:
    dir_path: ClassVar[str] = "models/meme_clf"

    @classmethod
    def meme_clf(cls, lts: bool):
        return EMemeClfVersion.LTS.value if lts else EMemeClfVersion.EDGE.value

    @classmethod
    def all_meme_clf_versions(cls):
        return list(os.listdir(cls.dir_path))

    @classmethod
    def reduce_to_meme_version(cls, meme_version: Optional[str], lts: Optional[bool]) -> str:
        assert (lts is not None and meme_version is None) or (lts is None and meme_version is not None), "provided both lts and meme_version"
        if lts is not None:
            meme_version = cls.meme_clf(lts)
        assert meme_version is not None  # and meme_version in cls.all_meme_clf_versions()
        return meme_version

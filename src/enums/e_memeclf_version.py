import os
from enum import Enum
from typing import Optional


class EMemeClfVersion(Enum):
    LTS = "0.0.7"
    EDGE = "0.0.8"

    @classmethod
    def get_root_dir_path(cls):
        return "models/meme_clf"

    @classmethod
    def all_meme_clf_versions(cls):
        return list(os.listdir(cls.get_root_dir_path()))

    @classmethod
    def get_version_by_lts(cls, lts: bool):
        return cls.LTS.value if lts else cls.EDGE.value

    @classmethod
    def reduce_to_meme_version(cls, meme_version: Optional[str], lts: Optional[bool]) -> str:
        assert (lts is not None and meme_version is None) or (lts is None and meme_version is not None), "provided both lts and meme_version"
        if lts is not None:
            meme_version = cls.get_version_by_lts(lts)
        assert meme_version is not None  # and meme_version in cls.all_meme_clf_versions()
        return meme_version

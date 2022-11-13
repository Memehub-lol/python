import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, TypeVar

from src.lib import decorators

Subclass = TypeVar("Subclass", bound="CheckpointBase")


@dataclass
class CheckpointBase:
    file_name: ClassVar[str]
    excluded_attrs: ClassVar[list[str]] = []
    meme_version: str

    @classmethod
    def _get_path(cls, meme_version: str, backup: bool) -> str:
        raise NotImplementedError()

    def _get_file_path(self, backup: bool):
        return f"{self._get_path(meme_version=self.meme_version, backup=backup)}/{self.file_name}"

    def _fresh_init(self):
        pass

    @classmethod
    def _dont_save_if_exists(cls) -> bool:
        return False

    @decorators.on_error_use_backup()
    def _load_from_disk(self, backup: bool):
        with open(self._get_file_path(backup), "rb") as f:
            state_dict: dict[Any, Any] = json.load(f)
        for k, v in state_dict.items():
            setattr(self, k, v)
        return self

    @classmethod
    def load(cls, meme_version: str, fresh: bool = False):
        self = cls(meme_version=meme_version)
        if not fresh:
            return self._load_from_disk(backup=False)
        self._fresh_init()
        self.save()
        return self

    def _get_state_dict(self):
        return {k: v for k, v in vars(self).items() if not k.startswith("_") and k not in self.excluded_attrs}

    @decorators.do_backup_also()
    def save(self, backup: bool = False) -> None:
        file_path = self._get_file_path(backup)
        if self._dont_save_if_exists() and Path(file_path).is_file():
            return
        Path(file_path).parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, "w") as f:
            json.dump(self._get_state_dict(), f)

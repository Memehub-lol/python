import json
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Protocol, TypeVar

from src.lib import decorators

Subclass = TypeVar("Subclass", bound="CheckpointBase")


class CheckpointProtocol(Protocol):
    file_name: ClassVar[str]
    excluded_attrs: ClassVar[list[str]]
    meme_version: str

    @classmethod
    def _get_path(cls, meme_version: str, backup: bool) -> str:
        ...


@dataclass
class CheckpointBase(CheckpointProtocol):
    file_name: ClassVar[str]
    excluded_attrs: ClassVar[list[str]] = []
    meme_version: str

    @classmethod
    def _get_path(cls, meme_version: str, backup: bool) -> str:
        raise NotImplementedError()

    @decorators.on_error_use_backup()
    def _load_from_disk(self, meme_version: str, backup: bool):
        path = self._get_path(meme_version=meme_version,  backup=backup)
        with open(path + f"/{self.file_name}", "rb") as f:
            state_dict = json.load(f)
        for k, v in state_dict.items():
            setattr(self, k, v)
        return self

    def _fresh_init(self):
        pass

    @classmethod
    def load(cls, meme_version: str, fresh: bool = False):
        self = cls(meme_version=meme_version)
        if not fresh:
            return self._load_from_disk(meme_version=meme_version,  backup=False)
        self._fresh_init()
        if cls._dont_save_if_exists():
            path = cls._get_path(meme_version=meme_version,  backup=False)
            if Path(path).is_file():
                return self
        self.save()
        return self

    def _dump_state_dict(self):
        return {k: v for k, v in vars(self).items() if not k.startswith("_") and k not in self.excluded_attrs}

    @classmethod
    def _dont_save_if_exists(cls) -> bool:
        return False

    @decorators.do_backup_also()
    def save(self, backup: bool = False) -> None:
        path = self._get_path(meme_version=self.meme_version, backup=backup)
        path += f"/{self.file_name}"
        Path(path).parent.mkdir(exist_ok=True, parents=True)
        with open(path, "w") as f:
            json.dump(self._dump_state_dict(), f)

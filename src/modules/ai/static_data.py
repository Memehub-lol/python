import json
from dataclasses import dataclass, field
from operator import itemgetter
from pathlib import Path
from typing import Any, ClassVar

from src.enums.e_memeclf_path import EMemeClfPath
from src.lib import decorators
from src.modules.template.template_service import TemplateService


@dataclass
class StaticData:
    file_name: ClassVar[str] = "static_data.json"
    num_images: ClassVar[int] = 10

    meme_version: str

    _all_names: list[str] = field(default_factory=list, init=False)
    _template_names: list[str] = field(default_factory=list, init=False)
    _num_name: dict[str, str] = field(default_factory=dict, init=False)

    def _fresh_init(self):
        self._name_num = {name: idx for idx, name in enumerate(TemplateService.get_train_names(self.num_images))}
        max_num = max(*list(self._name_num.values()))
        self._name_num["not_meme"] = max_num+1
        self._name_num["not_template"] = max_num+2

    def _get_num_name(self):
        if not self.num_name:
            self.num_name = {str(v): k for k, v in self._name_num.items()}
        return self.num_name

    def get_num(self, name: str):
        return self._name_num[name]

    def get_name(self, num: int):
        return self._get_num_name()[str(num)]

    def get_names(self, int_names: list[str]):
        return itemgetter(*int_names)(self._get_num_name())

    def get_all_names(self):
        if not self.all_names:
            self.all_names = list(self._name_num.keys())
        return self.all_names

    def get_template_names(self):
        if not self._template_names:
            self._template_names = list(filter(lambda name: name not in ["not_meme", "not_template"], self._name_num.keys()))
        return self._template_names

    @decorators.do_backup_also()
    def save(self, backup: bool = False) -> None:
        file_path = self._get_file_path(backup)
        if Path(file_path).is_file():
            return
        Path(file_path).parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, "w") as f:
            json.dump({"file_name": self.file_name,
                       "meme_version": self.meme_version,
                       "_name_num": self._name_num}, f)

    @classmethod
    def load(cls, meme_version: str, fresh: bool = False):
        self = cls(meme_version=meme_version)
        if not fresh:
            return self._load_from_disk(backup=False)
        self._fresh_init()
        self.save()
        return self

    @decorators.on_error_use_backup()
    def _load_from_disk(self, backup: bool):
        with open(self._get_file_path(backup), "rb") as f:
            state_dict: dict[Any, Any] = json.load(f)
        for k, v in state_dict.items():
            setattr(self, k, v)
        return self

    def _get_file_path(self, backup: bool):
        return f"{EMemeClfPath.path_by_version(self.meme_version, backup)}/{self.file_name}"

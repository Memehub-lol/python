from dataclasses import dataclass
from typing import ClassVar, Optional, TypedDict

from src.lib.json_save_load_base import CheckpointBase
from src.modules.ai.meme_clf.lib.meme_clf_path import MemeClfPath
from src.modules.template.template_service import TemplateService


class NameToMax(TypedDict):
    not_meme: int
    not_template: int
    template: dict[str, int]


class TestTrainToMax(TypedDict):
    train: NameToMax
    test: NameToMax


def get_name_num_live(num_images: int = 10):
    return {name: idx for idx, name in enumerate(TemplateService.get_train_names(num_images))}


@dataclass
class StaticData(CheckpointBase):
    file_name: ClassVar[str] = "static_data.json"
    excluded_attrs: ClassVar[list[str]] = ["all_names", "template_names", "num_name"]
    meme_version: str

    @classmethod
    def _dont_save_if_exists(cls):
        return True

    @classmethod
    def _get_path(cls, meme_version: str, backup: bool, stonk_version: Optional[str] = None, name: Optional[str] = None):
        return MemeClfPath.meme_clf_path(meme_verion=meme_version, backup=backup)

    def _fresh_init(self):
        self.name_num = get_name_num_live()
        max_num = max(*list(self.name_num.values()))
        self.name_num["not_meme"] = max_num+1
        self.name_num["not_template"] = max_num+2

    def get_num_name(self):
        if not getattr(self, "num_name", None):
            self.num_name = {str(v): k for k, v in self.name_num.items()}
        return self.num_name

    def get_num(self, name: str):
        return self.name_num[name]

    def get_name(self, num: int):
        return self.get_num_name()[str(num)]

    def get_all_names(self):
        if not getattr(self, "all_names", None):
            self.all_names = self.name_num.keys()
        return self.all_names

    def get_template_names(self):
        if not getattr(self, "template_names", None):
            self.template_names = list(filter(lambda name: name not in ["not_meme", "not_template"], self.name_num.keys()))
        return self.template_names

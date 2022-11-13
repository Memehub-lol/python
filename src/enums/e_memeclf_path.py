from enum import Enum

from src.enums.e_memeclf_version import EMemeClfVersion


class EMemeClfPath(Enum):
    MODEL_STATS = "model_stats"
    JIT_CPU = "jit_cpu"
    JIT_GPU = "jit_gpu"
    REG = "reg"

    @classmethod
    def get_root_dir_path(cls):
        return EMemeClfVersion.get_root_dir_path()

    @classmethod
    def path_by_version(cls, meme_verion: str, *, backup: bool):
        path = f"{cls.get_root_dir_path()}/{meme_verion}"
        return path.replace("models", "models/backup") if backup else path

    def build_path_by_version(self, meme_version: str, *, backup: bool):
        path = f"{self.get_root_dir_path()}/{meme_version}/{self.value}"
        return path.replace("models", "models/backup") if backup else path

    def build_path_by_lts(self, lts: bool, *, backup: bool):
        return self.build_path_by_version(EMemeClfVersion.get_version_by_lts(lts), backup)

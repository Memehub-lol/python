from enum import Enum

from src.modules.versioning import Versioner


class ESaveFolder(Enum):
    MODEL_STATS = "model_stats"
    JIT_CPU = "jit_cpu"
    JIT_GPU = "jit_gpu"
    REG = "reg"


class MemeClfPath:
    root_dir = "models/meme_clf"

    @classmethod
    def meme_clf_path(cls, meme_verion: str, backup: bool):
        path = cls.root_dir + f"/{meme_verion}"
        return path.replace("models", "models/backup") if backup else path

    @classmethod
    def build_path_by_version(cls, e_save_folder: ESaveFolder, meme_version: str, backup: bool):
        path = cls.root_dir + f"/{meme_version}/{e_save_folder.value}"
        return path.replace("models", "models/backup") if backup else path

    @classmethod
    def build_path_by_lts(cls, e_save_folder: ESaveFolder, lts: bool, backup: bool):
        return cls.build_path_by_version(e_save_folder, Versioner.meme_clf(lts), backup)

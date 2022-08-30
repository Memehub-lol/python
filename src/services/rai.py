import os
from typing import Any, cast

import ml2rt
from src.modules.versioning import Versioner
from redisai.client import Client
from src.lib import logger
from src.modules.ai.meme_clf.lib.meme_clf_path import ESaveFolder, MemeClfPath
from torch import cuda

from src.services.environment import Environment


class Rai:
    backend = "TORCH"
    client = Client(**Environment.REDIS_AI_CONFIG)

    @classmethod
    def delete(cls, name: str):
        _ = cls.client.modeldel(name)

    @classmethod
    def modelstore(cls, name: str, model: Any, tag: str):
        try:
            _ = cls.client.modelstore(name,
                                      Rai.backend,
                                      Environment.REDIS_AI_DEVICE,
                                      model,
                                      tag=tag,
                                      inputs=cast(Any, None),
                                      outputs=cast(Any, None))
            logger.info("Loaded %s", name)
        except Exception as e:
            logger.error("FAILED - %s", name)
            raise e

    @classmethod
    def get_currently_loaded(cls, tags: list[str]):
        names_in_redis: set[str] = set()
        for name, tag in cls.client.modelscan():
            names_in_redis.add(cast(str, name)) if tag in tags else cls.client.modeldel(name)
        return names_in_redis

    @classmethod
    def load_models_to_redis(cls, reload: bool):
        meme_version = Versioner.meme_clf(lts=True)
        folder = ESaveFolder.JIT_GPU if cuda.is_available() else ESaveFolder.JIT_CPU
        jit_folder = "./" + MemeClfPath.build_path_by_version(folder, meme_version, backup=False)
        maybe_names_in_redis: set[str] = cls.get_currently_loaded([meme_version]) if not reload else set()
        logger.info("Loading MemeClf to redisai")
        names_on_disk = set([os.path.splitext(filename)[0] for filename in os.listdir(jit_folder)])
        for name in names_on_disk - maybe_names_in_redis:
            model: Any = ml2rt.load_model(f"{jit_folder}/{name}.pt")
            cls.modelstore(name, model, meme_version)
        for name in maybe_names_in_redis - names_on_disk:
            cls.delete(name)

from typing import Any, cast

from redisai.client import Client
from src.lib import logger
from torch import cuda


class RedisConfig:
    host = "redisai"
    port = 6379


class Rai:
    backend = "TORCH"
    device = "GPU" if cuda.is_available() else "CPU"

    @classmethod
    def get_client(cls):
        return Client(host=RedisConfig.host, port=RedisConfig.port)

    @classmethod
    def modelstore(cls, name: str, model: Any, tag: str):
        client = cls.get_client()
        try:
            _ = client.modelstore(name,
                                  Rai.backend,
                                  Rai.device,
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
        client = cls.get_client()
        names_in_redis: set[str] = set()
        for name, tag in client.modelscan():
            names_in_redis.add(cast(str, name)) if tag in tags else client.modeldel(name)
        return names_in_redis

import json
import os
from enum import Enum
from typing import Literal, TypedDict, cast

from torch import cuda, device


class EnvVars(TypedDict):
    FLASK_ENV: Literal["local"] | Literal["development"] | Literal["staging"] | Literal["production"]
    ORIGIN_WHITELIST: str
    SECRET: str

    REDIS_MOD_HOST: str
    REDIS_MOD_PORT: str

    REDIS_AI_HOST: str
    REDIS_AI_PORT: str

    AWS_ID: str
    AWS_KEY: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    REDDIT_OAUTH_0: str
    REDDIT_OAUTH_1: str
    REDDIT_OAUTH_2: str
    REDDIT_OAUTH_3: str
    REDDIT_OAUTH_4: str
    REDDIT_OAUTH_5: str
    REDDIT_OAUTH_6: str
    REDDIT_OAUTH_7: str


class Environment:
    _env_vars = cast(EnvVars, os.environ)

    IS_PROD = _env_vars["FLASK_ENV"] == "production"
    ORIGIN_WHITELIST = json.loads(_env_vars["ORIGIN_WHITELIST"])

    FLASK_CONFIG = (_env_vars["SECRET"], _env_vars["FLASK_ENV"], IS_PROD)
    REDIS_AI_CONFIG = {"host": _env_vars['REDIS_AI_HOST'], "port": _env_vars['REDIS_AI_PORT']}
    REDIS_MOD_CONFIG = {"host": _env_vars['REDIS_MOD_HOST'], "port": _env_vars['REDIS_MOD_PORT']}

    REDIS_MOD_URL = f"redis://{REDIS_MOD_CONFIG['host']}:{REDIS_MOD_CONFIG['port']}"
    RABBIT_MQ_URL = "pyamqp://rabbitmq:5672"

    PYTORCH_DEVICE = device("cuda:0" if cuda.is_available() else "cpu")
    REDIS_AI_DEVICE = "GPU" if cuda.is_available() else "CPU"

    AWS_CONFIG = (_env_vars["AWS_ID"], _env_vars["AWS_KEY"], "memehub-development")

    @classmethod
    def get_site_db_connection_options(cls):
        return ("postgresql",
                cls._env_vars["POSTGRES_USER"],
                cls._env_vars["POSTGRES_PASSWORD"],
                cls._env_vars["POSTGRES_HOST"],
                cls._env_vars["POSTGRES_PORT"],
                cls._env_vars["POSTGRES_DB"])

    @classmethod
    def get_training_db_connection_options(cls):
        return ("postgresql",
                cls._env_vars["POSTGRES_USER"],
                cls._env_vars["POSTGRES_PASSWORD"],
                cls._env_vars["POSTGRES_HOST"],
                cls._env_vars["POSTGRES_PORT"],
                cls._env_vars["POSTGRES_DB"])

    @classmethod
    def get_reddit_oauths(cls):
        return [cls._env_vars["REDDIT_OAUTH_0"],
                cls._env_vars["REDDIT_OAUTH_1"],
                cls._env_vars["REDDIT_OAUTH_2"],
                cls._env_vars["REDDIT_OAUTH_3"],
                cls._env_vars["REDDIT_OAUTH_4"],
                cls._env_vars["REDDIT_OAUTH_5"],
                cls._env_vars["REDDIT_OAUTH_6"],
                cls._env_vars["REDDIT_OAUTH_7"]]

class Database(Enum):
    SITE = "SITE"
    TRAINING = "TRAINING"

    def get_config(self):
        if self is Database.SITE:
            return Environment.get_site_db_connection_options()
        elif self is Database.TRAINING:
            return Environment.get_training_db_connection_options()
        raise Exception("enum exhausted")

    def url(self):
        protocol, user, password, host, port, db_Name = self.get_config()
        return f"{protocol}://{user}:{password}@{host}:{port}/{db_Name}"

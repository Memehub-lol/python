import json
import os
from typing import Literal, TypedDict, Union, cast

from torch import cuda, device


class EnvVars(TypedDict):
    FLASK_ENV: Union[Literal["local"], Literal["development"], Literal["staging"], Literal["production"]]
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
    TRAINING_POSTGRES_PORT: str
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
    IS_LOCAL = _env_vars["FLASK_ENV"] == "local"
    ORIGIN_WHITELIST = json.loads(_env_vars["ORIGIN_WHITELIST"])

    FLASK_CONFIG = (_env_vars["SECRET"], _env_vars["FLASK_ENV"], IS_PROD)
    REDIS_AI_CONFIG = {"host": _env_vars['REDIS_AI_HOST'], "port": _env_vars['REDIS_AI_PORT']}
    REDIS_MOD_CONFIG = {"host": _env_vars['REDIS_MOD_HOST'], "port": _env_vars['REDIS_MOD_PORT']}

    REDIS_MOD_URL = f"redis://{REDIS_MOD_CONFIG['host']}:{REDIS_MOD_CONFIG['port']}"
    RABBIT_MQ_URL = "pyamqp://rabbitmq:5672"

    PYTORCH_DEVICE = device("cuda:0" if cuda.is_available() else "cpu")
    REDIS_AI_DEVICE = "GPU" if cuda.is_available() else "CPU"

    AWS_CONFIG = {"AWS_ID": _env_vars["AWS_ID"],
                  "AWS_KEY": _env_vars["AWS_KEY"],
                  "BUCKET": "memehub-development"}

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
                "localhost",
                cls._env_vars["TRAINING_POSTGRES_PORT"],
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

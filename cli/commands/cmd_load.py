import os
from typing import Any

import click
import ml2rt
from src.lib import logger
from src.lib.services.rai import Rai
from src.lib.versioning import Versioner
from src.modules.ai.meme_clf.lib.meme_clf_path import ESaveFolder, MemeClfPath
from torch import cuda


@click.group()
def load():
    """ Run Imgflip Related Scripts"""
    pass


@load.command()
@click.option("-r", "--reload", type=bool, default=False, required=False)
def stonk_market(reload: bool):
    """
    Load Stonk models into redisai
    """
    meme_version = Versioner.meme_clf(lts=True)
    folder = ESaveFolder.JIT_GPU if cuda.is_available() else ESaveFolder.JIT_CPU
    jit_folder = "./" + MemeClfPath.build_path_by_version(folder, meme_version, backup=False)
    maybe_names_in_redis: set[str] = Rai.get_currently_loaded([meme_version]) if not reload else set()
    logger.info("Loading MemeClf to redisai")
    names_on_disk = set([os.path.splitext(filename)[0] for filename in os.listdir(jit_folder)])
    for name in names_on_disk - maybe_names_in_redis:
        model: Any = ml2rt.load_model(f"{jit_folder}/{name}.pt")
        Rai.modelstore(name, model, meme_version)

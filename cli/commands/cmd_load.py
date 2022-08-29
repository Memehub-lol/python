

import click
from src.services.rai import Rai


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
    Rai.load_models_to_redis(reload)

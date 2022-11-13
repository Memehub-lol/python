import subprocess

import click
from src.enums.e_database import EDatabase


@click.command()
def gen2():
    """
    Runs Arbitrary Scripts from Scripts Folder

    Arguments:
        name {[type]} -- filename without ext
    """

    folder = "src/generated"
    cmd1 = f"sqlacodegen --generator dataclasses --outfile {folder}/training_dataclasses.py {EDatabase.TRAINING.url()}"
    cmd2 = f"sqlacodegen --outfile {folder}/training_tables.py {EDatabase.TRAINING.url()}"

    return subprocess.call(f"{cmd1} && {cmd2}", shell=True)

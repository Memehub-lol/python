import subprocess

import click
from src.services.database import Database


@click.command()
def gen():
    """
    Runs Arbitrary Scripts from Scripts Folder

    Arguments:
        name {[type]} -- filename without ext
    """

    folder = "src/modules/generated"
    cmd1 = f"sqlacodegen --generator dataclasses --outfile {folder}/site_dataclasses.py {Database.SITE.url()}"
    cmd2 = f"sqlacodegen --outfile {folder}/site_tables.py {Database.SITE.url()}"

    return subprocess.call(f"{cmd1} && {cmd2}", shell=True)

import subprocess

import click
from src.lib.services.database import Database, DatabaseConfig


@click.command()
def gen():
    """
    Runs Arbitrary Scripts from Scripts Folder

    Arguments:
        name {[type]} -- filename without ext
    """

    folder = "src/modules/generated/"
    cmd1 = f"sqlacodegen --generator dataclasses --outfile {folder}site_dataclasses.py {DatabaseConfig.url(Database.SITE)}"
    cmd2 = f"sqlacodegen --outfile {folder}site_tables.py {DatabaseConfig.url(Database.SITE)}"

    return subprocess.call(cmd1+" && "+cmd2, shell=True)

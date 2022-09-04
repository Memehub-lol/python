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
    tables = "--tables reddit_memes,redditors,reddit_scores,imgflip_templates"
    cmd1 = f"sqlacodegen {tables} --generator dataclasses --outfile {folder}/site_dataclasses.py {Database.SITE.url()}"
    cmd2 = f"sqlacodegen {tables} --outfile {folder}/site_tables.py {Database.SITE.url()}"

    return subprocess.call(f"{cmd1} && {cmd2}", shell=True)

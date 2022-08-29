

import subprocess

import click


@click.group()
def migration():
    """ Run Imgflip Related Scripts"""
    pass


@migration.command()
@click.option("-n", "--name", type=str, required=True)
def gen(name: str):
    """
    Generate Flask migration
    """

    cmd = f'alembic revision --autogenerate -m "{name}"'

    return subprocess.call(cmd, shell=True)


@migration.command()
def run():
    """
    Run Flask migration
    """

    cmd = 'alembic -c alembic.docker.ini upgrade head'

    return subprocess.call(cmd, shell=True)

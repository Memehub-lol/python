

import subprocess

import click


@click.command()
@click.option("-n", "--name", type=str, required=True, default="init")
def migrate(name: str):
    """
    Run Flask migration
    """

    cmd = f'alembic revision --autogenerate -m "{name}"'

    return subprocess.call(cmd, shell=True)

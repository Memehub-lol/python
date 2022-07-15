import click
from src.lib.services.aws import AWS


@click.group()
def aws():
    """ Run AWS Related Scripts"""
    pass


@aws.command()
def upload_folder():
    AWS.upload_folder("aws/", "frontend/")


@aws.command()
def upload_memes():
    AWS.upload_folder("data/memes/", "faker/memes/", stem=True)

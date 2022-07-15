import click
from src.modules.template.template_service import TemplateService


@click.group()
def templates():
    """ Run Imgflip Related Scripts"""
    pass


@templates.command()
def sync():
    if TemplateService.repo.count():
        return
    TemplateService.build_db()

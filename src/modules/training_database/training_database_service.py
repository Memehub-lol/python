import os
import shutil
from enum import Enum
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy import delete, select
from sqlalchemy.orm.session import Session
from src.lib import logger, utils
from src.lib.image_url import ImageUrlUtils
from src.services.database import (site_session_maker,
                                   training_session_maker)
from src.lib.template_data import REPLICATED_TEMPLATES_GROUPED
from src.modules.generated.site_dataclasses import Templates as TemplatesDC
from src.modules.generated.site_tables import Templates
from src.modules.training_database.training_database_entities import (
    NotMemeEntity, NotTemplateEntity, TemplateEntity, training_entities)

num_pages = 1000


class EDataPath(Enum):
    NOT_MEME = "data/not_a_meme"
    NOT_TEMPLATE = "data/reddit/not_template"
    IMGFLIP = "data/imgflip"
    INCORRECT = "data/incorrect"
    REDDIT = "data/reddit"

    @classmethod
    def get_reddit_path(cls, name: str, url: str):
        return f"{EDataPath.REDDIT.value}/{name}/{url.split('/')[-1]}"

    def folder(self, name: str):
        return f"{self.value}/{name}"

    def path(self, name: str, filename: str):
        return f"{self.value}/{name}/{filename}"


with site_session_maker() as session:
    templates: list[TemplatesDC] = session.scalars(select(Templates)).all()


def add_path_urls_from_page(page_num: int):
    for template in templates:
        try:
            with requests.get(template.page.format(page_num)) as resp:
                soup = BeautifulSoup(resp.text, "lxml")
            for meme_element in soup.find_all("img", class_="base-img"):
                url = "https:" + meme_element["src"]
                path = EDataPath.IMGFLIP.path(template.name, url.split("/")[-1])
                _ = ImageUrlUtils.download_image(url, path, verbose=True)
        except:
            pass


class TrainingDatabaseService:
    @classmethod
    def folder_count(cls):
        series = pd.Series({folder: len(os.listdir(EDataPath.IMGFLIP.value+folder)) for folder in os.listdir(EDataPath.IMGFLIP.value)})
        utils.display_df(series.sort_values(ascending=True)[:25])

    @classmethod
    def download_images_from_imgflip(cls):
        for template in templates:
            Path(EDataPath.IMGFLIP.value + "/" + template.name).mkdir(parents=True, exist_ok=True)
        _ = utils.process(add_path_urls_from_page, range(num_pages), total=num_pages)

    @classmethod
    def _clear_training_data(cls, session: Session):
        for entity in training_entities:
            _ = session.execute(delete(entity))
        session.commit()

    @classmethod
    def _add_not_template(cls, session: Session):
        for idx, filename in enumerate(os.listdir(EDataPath.NOT_TEMPLATE.value)):
            session.add(NotTemplateEntity(is_test_set=idx % 10 == 0, path=f"{EDataPath.NOT_TEMPLATE.value}/{filename}"))
        session.commit()

    @classmethod
    def _add_not_meme(cls, session: Session):
        for idx, filename in enumerate(os.listdir(EDataPath.NOT_MEME.value)):
            session.add(NotMemeEntity(is_test_set=idx % 10 == 0, path=f"{EDataPath.NOT_MEME.value}/{filename}"))
        session.commit()

    @classmethod
    def _add_templates(cls, session: Session):
        for template in templates:
            imgflip_path = EDataPath.IMGFLIP.folder(template.name)
            Path(imgflip_path).mkdir(parents=True, exist_ok=True)
            for idx, filename in enumerate(os.listdir(imgflip_path)):
                path = EDataPath.IMGFLIP.path(template.name, filename)
                session.add(TemplateEntity(is_test_set=idx % 10 == 0, name=template.name, path=path))
            reddit_path = EDataPath.REDDIT.folder(template.name)
            Path(reddit_path).mkdir(parents=True, exist_ok=True)
            for filename in os.listdir(reddit_path):
                path = EDataPath.REDDIT.path(template.name, filename)
                session.add(TemplateEntity(is_test_set=False, name=template.name, path=path))
        session.commit()

    @classmethod
    def _add_template_image_count(cls, session: Session):
        for template in session.scalars(select(Templates)):
            files = os.listdir(EDataPath.IMGFLIP.folder(template.name)) + os.listdir(EDataPath.REDDIT.folder(template.name))
            template.num_images = len(files)
        session.commit()

    @classmethod
    def build_db(cls):
        with training_session_maker() as session:
            cls._clear_training_data(session)
            cls._add_not_template(session)
            cls._add_not_meme(session)
            cls._add_templates(session)
        with site_session_maker() as session:
            cls._add_template_image_count(session)

    @staticmethod
    def clean_data():
        bad_folders: list[str] = []
        for names in REPLICATED_TEMPLATES_GROUPED:
            Path(dest := EDataPath.IMGFLIP.folder(names[-1]) + "/").mkdir(parents=True, exist_ok=True)
            for name in names[:-1]:
                path = EDataPath.IMGFLIP.folder(name) + "/"
                if not Path(path).is_dir():
                    bad_folders.append(name)
                    continue
                if not len(os.listdir(path)):
                    shutil.rmtree(path)
                for filename in Path(path).iterdir():
                    try:
                        _ = shutil.copyfile(filename, dest + filename.stem)
                    except shutil.SameFileError:
                        pass
        logger.info("bad folders", bad_folders)

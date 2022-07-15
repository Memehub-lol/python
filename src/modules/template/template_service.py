from functools import partial
from typing import Any, cast

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select
from src.lib import logger, utils
from src.lib.template_data import (DONT_USE_TEMPLATES,
                                   REPLICATED_TEMPLATES_GROUPED,
                                   USER_TEMPLATES)
from src.modules.generated.site_tables import Templates
from src.modules.template.template_repo import TemplateRepo


def adjust_for_alt(name: str):
    return REPLICATED_TEMPLATES_GROUPED[name] if name in REPLICATED_TEMPLATES_GROUPED else name


def sanitize_template_name(name: str) -> str:
    filtered = "".join(i for i in name.encode("ascii", "ignore").decode() if i not in ":*?<>|.'()_/")
    return filtered.strip().lower().replace(",", " ").replace(", ", " ").replace('"', '')


def scrape_template_data(page_number: int, db_names: dict[str, int]):
    templates = cast(list[dict[str, Any]], USER_TEMPLATES)
    with requests.get(f"https://imgflip.com/memetemplates?page={page_number}") as resp:
        soup = BeautifulSoup(resp.text, "lxml")
    for meme in soup.find_all("div", class_="mt-img-wrap"):
        title = meme.a["title"][:-5]
        imgflip_name = sanitize_template_name(title)
        name = adjust_for_alt(imgflip_name)
        page = "https://imgflip.com" + meme.a["href"] + "?page={}"
        url = "https:" + meme.a.img["src"]
        if name not in DONT_USE_TEMPLATES:
            templates.append(dict(name=name, page=page, url=url, imgflip_name=imgflip_name))
    maybe_filtered = filter(lambda template: template["imgflip_name"] not in db_names, templates) if db_names else templates
    return list(TemplateRepo.Dataclass(**template_data) for template_data in maybe_filtered)


class TemplateService:
    repo = TemplateRepo

    @classmethod
    def get_train_names(cls, num_images: int) -> list[str]:
        with TemplateRepo.sessionmaker() as session:
            q = (select(Templates.name)
                 .where(Templates.num_images >= num_images)
                 .where(Templates.name == Templates.imgflip_name))
            return session.scalars(q).all()

    @classmethod
    def build_db(cls, clear: bool = False):
        num_pages = 250
        with TemplateRepo.sessionmaker() as session:
            result = session.execute(select(Templates.imgflip_name.distinct())).scalars()
        db_names: dict[str, int] = {name: idx for idx, name in enumerate(result)}
        templates = utils.process_from_iterable(partial(scrape_template_data, db_names=db_names),
                                                range(num_pages),
                                                total=num_pages,
                                                multi=False,
                                                label="imgflip template scrapper")
        with TemplateRepo.sessionmaker() as session:
            session.add_all({template.name: template for template in templates}.values())
        logger.info(f"Total Templates: {TemplateRepo.count()}")

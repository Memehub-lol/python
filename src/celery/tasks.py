from src.celery import CELERY
from src.celery.config import CELERYBEAT_SCHEDULE
from src.lib import logger
from src.modules.reddit_meme.reddit_meme_service import RedditMemeService
from src.modules.template.template_service import TemplateService


@CELERY.task(name=CELERYBEAT_SCHEDULE["ai"]["task"], unique_on=[], lock_expiry=60 * 60 * 12)
def model_runner():
    logger.info("AiModelRunner Unimplemented")
    return
    # logger.info("AiModelRunner Task Started")
    # models = Rai.get_client().modelscan()
    # if not models or Versioner.meme_clf(lts=True) != models[0][1]:
    #     return
    # ModelRunner(entity=Entity.RedditMeme, is_celery=True).execute(0)
    # ModelRunner(entity=Entity.Meme,is_celery=True).execute()


@CELERY.task(name=CELERYBEAT_SCHEDULE["reddit"]["task"], unique_on=[], lock_expiry=60 * 60 * 12)
def Reddit():
    logger.info("Reddit Scraper Task Started")
    RedditMemeService.praw_memes(verbose=False)
    RedditMemeService.calc_percentiles(verbose=False)


@CELERY.task(name=CELERYBEAT_SCHEDULE["template"]["task"], unique_on=[], lock_expiry=60 * 60 * 12)
def template_syncer():
    logger.info("Template Sync Task Started")
    if TemplateService.repo.count():
        return
    TemplateService.build_db()

from src.celery import CELERY
from src.celery.config import CELERYBEAT_SCHEDULE
from src.lib import logger
from src.modules.reddit_meme.reddit_scraper import calc_percentiles, praw_memes


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
    praw_memes(verbose=False)
    calc_percentiles()

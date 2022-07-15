from src.modules.reddit_meme.reddit_scraper import RedditMemeScrapper


class RedditMemeService:
    @classmethod
    def praw_memes(cls, verbose: bool = True, multi: bool = True, use_billard: bool = True):
        RedditMemeScrapper.praw_memes(verbose, multi, use_billard)

    @classmethod
    def calc_percentiles(cls, verbose: bool = True):
        RedditMemeScrapper.calc_percentiles(verbose)

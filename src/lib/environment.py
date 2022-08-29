import os

from torch import cuda, device


class Environment:
    device = device("cuda:0" if cuda.is_available() else "cpu")
    is_prod = os.environ["FLASK_ENV"] == "production"
    whitelist = ["http://localhost", "https://backend.memehub.lol"]

    @classmethod
    def get_reddit_oauths(cls):
        reddit_oauths: list[str] = []
        i = 0
        while True:
            oauth_str = os.environ.get(f"REDDIT_OAUTH_{i}")
            if oauth_str is None:
                break
            reddit_oauths.append(oauth_str)
            i += 1
        assert reddit_oauths, f"reddit_oauths {reddit_oauths}"
        return reddit_oauths

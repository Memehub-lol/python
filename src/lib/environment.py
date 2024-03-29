import os

from dotenv import load_dotenv
from torch import cuda, device

_ = load_dotenv()


class Environment:
    is_docker = bool(int(os.environ["IS_DOCKER"]))
    device = device("cuda:0" if cuda.is_available() else "cpu")
    is_prod = os.environ["FLASK_ENV"] == "production"
    whitelist = ["http://localhost", "https://backend.memehub.lol"]

    @classmethod
    def get_reddit_oauths(cls):
        reddit_oauths: list[str] = []
        i = 0
        while True:
            oauth_str = os.environ.get(f"reddit_oauth_{i}")
            if oauth_str is None:
                break
            reddit_oauths.append(oauth_str)
            i += 1
        return reddit_oauths

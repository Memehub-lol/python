import json
from typing import Any, Dict, List

import requests
from retry import retry
from src.lib import logger


@retry(tries=5, delay=1, logger=logger, backoff=1)
def make_request(url: str) -> Dict[str, List[Dict[str, Any]]]:
    with requests.get(url) as resp:
        if resp.status_code != 200:
            logger.error(url)
            logger.error(resp.content)
        return json.loads(resp.content)

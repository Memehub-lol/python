from logging import Logger
from pathlib import Path
from typing import cast

import logzero

# log_path = "logs/logfile.log"
# Path(log_path).mkdir(exist_ok=True, parents=True)

# logzero.logfile(
#     log_path,
#     maxBytes=1_000_000,
#     backupCount=3,
#     # loglevel=logzero.ERROR,
#     # disableStderrLogger=True
# )

# logger is used internally as a module exposing functions like info, debug, error, warning
# the implementation used is logzero - https://logzero.readthedocs.io/en/latest/
logger = cast(Logger,logzero.logger)

import time
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class Timer:
    round_start: int = field(default_factory=lambda: int(time.time()))
    exec_start: int = field(default_factory=lambda: int(time.time()))
    uptime: int = 0
    train_runtime: int = 0
    round_runtime: int = 0

    @contextmanager
    def is_training(self):
        start = time.time()
        yield
        self.train_runtime = int(time.time()-start)

    def new_round(self):
        self.round_runtime = int(time.time()) - self.round_start
        self.round_start = int(time.time())
        self.uptime = int(time.time() - self.exec_start)

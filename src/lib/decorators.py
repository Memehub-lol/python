import time
from functools import wraps
from typing import Any, Callable, TypeVar

from src.lib import logger, utils

ReturnType = TypeVar('ReturnType')
Decorator = Callable[[Callable[..., ReturnType]], Callable[..., ReturnType]]


def timeit() -> Decorator[ReturnType]:
    """
    Use this decorator to debug running time of any method.
    Usage:
        Add @timeit on top of the function you want to time
    """
    def decorator(f: Callable[..., ReturnType]):
        @wraps(f)
        def wrapped(*args: Any, **kw: Any):
            t_start = time.time()
            result = f(*args, **kw)
            t_end = time.time()
            logger.info('%s: %s ms', f.__name__, utils.secondsToText(int(t_end-t_start)))
            return result
        return wrapped
    return decorator


def on_error_use_backup() -> Decorator[ReturnType]:
    def decorator(f: Callable[..., ReturnType]):
        @wraps(f)
        def wrapped(*args: Any, backup: bool, **kwargs: Any):
            try:
                return f(*args, backup=True, **kwargs)
            except Exception:
                pass
            try:
                return f(*args, backup=False, **kwargs)
            except Exception as e:
                logger.error(f"LOADING FAILED on_error_use_backup, args: {args[1:]}, kwargs: {kwargs}")
                raise e
        return wrapped
    return decorator


def do_backup_also() -> Decorator[None]:
    def decorator(f: Callable[..., None]):
        @wraps(f)
        def wrapped(*args: Any, **kwargs: Any):
            _ = f(*args, backup=True, **kwargs)
            _ = f(*args, backup=False, **kwargs)
        return wrapped
    return decorator

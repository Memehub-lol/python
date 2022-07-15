import time
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from src.lib import logger, utils

ReturnType = TypeVar('ReturnType')
Decorator = Callable[[Callable[..., ReturnType]], Callable[..., ReturnType]]


def report_exception(raise_exception: bool = False,
                     msg: str = "",
                     return_value: Optional[ReturnType] = None) -> Decorator[ReturnType]:
    def decorator(f: Callable[..., ReturnType]):
        @wraps(f)
        def wrapped(*args: Any, **kwargs: Any):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                if msg:
                    logger.error(msg)
                else:
                    logger.error("func name: "+f.__name__+"\n"+str(e))
                if raise_exception:
                    raise e
                else:
                    return return_value
        return wrapped
    return decorator


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


def lts_safe() -> Decorator[ReturnType]:
    def decorator(f: Callable[..., ReturnType]):
        @wraps(f)
        def wrapped(*args: Any, lts: bool, fresh: bool, **kwargs: Any):
            assert not lts or not fresh
            return f(*args, lts=lts, fresh=fresh, **kwargs)
        return wrapped
    return decorator

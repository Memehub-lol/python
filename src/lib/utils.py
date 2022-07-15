import json
from datetime import datetime
from itertools import chain
from multiprocessing import Pool as MpPool
from multiprocessing import cpu_count as MpCpu_count
from multiprocessing.pool import Pool as mpPoolType
from typing import Any, Callable, Dict, Iterable, List, Optional, TypeVar, cast

import numpy as np
import pandas as pd
import requests
from billiard import Pool, cpu_count  # type:ignore
from IPython.core.display import clear_output
from IPython.display import display
from pandas import option_context
from pandas.core.frame import DataFrame
from pandas.core.generic import NDFrame
from pandas.core.series import Series
from retry import retry
from src.lib import logger
from tqdm import tqdm

ReturnType = TypeVar("ReturnType")


def process(func: Callable[..., Optional[ReturnType]],
            iterable: Iterable[Any],
            multi: bool = True,
            verbose: bool = True,
            use_billard: bool = False,
            label: Optional[str] = None,
            total: Optional[int] = None,
            distinct: bool = False,
            num_workers: Optional[int] = None) -> List[ReturnType]:
    def isNotNone(result: Optional[ReturnType]):
        return result is not None

    def wrapper(gen: Iterable[Optional[ReturnType]]):
        return list(cast(Iterable[ReturnType], filter(isNotNone, gen)))

    def distinct_wrapper(gen: Iterable[Optional[ReturnType]]) -> list[ReturnType]:
        return list(cast(Iterable[ReturnType], filter(isNotNone, set(gen))))
    run_generator = distinct_wrapper if distinct else wrapper
    if not multi:
        if verbose:
            if total:
                results = run_generator(tqdm((func(item) for item in iterable), desc=label, total=total))
            else:
                results = run_generator(tqdm((func(item) for item in iterable), desc=label))
        else:
            results = run_generator((func(item) for item in iterable))
    else:
        with cast(mpPoolType, Pool(num_workers or cpu_count())) if use_billard else MpPool(num_workers or MpCpu_count()) as workers:
            if verbose:
                if total:
                    results = run_generator(tqdm(workers.imap_unordered(func, iterable), desc=label, total=total))
                else:
                    results = run_generator(tqdm(workers.imap_unordered(func, iterable), desc=label))
            else:
                results = run_generator(workers.imap_unordered(func, iterable))
    return results


def process_from_iterable(func: Callable[..., Iterable[ReturnType]],
                          iterable: Iterable[Any],
                          multi: bool = True,
                          verbose: bool = True,
                          use_billard: bool = False,
                          label: Optional[str] = None,
                          total: Optional[int] = None,
                          distinct: bool = False) -> List[ReturnType]:
    data = chain.from_iterable(process(func, iterable, multi=multi, verbose=verbose, distinct=False, use_billard=use_billard, label=label, total=total))
    return list(set(data)) if distinct else list(data)


@retry(tries=5, delay=1, logger=logger, backoff=1)
def make_request(url: str) -> Dict[str, List[Dict[str, Any]]]:
    with requests.get(url) as resp:
        # if resp.status_code != 200:
        #     logger.error(url)
        #     logger.error(resp)
        return json.loads(resp.content)


def avg_n(listy: List[float], avg: int) -> List[float]:
    return [np.mean(listy[i: i + avg]) for i in range(0, len(listy), avg)]


@option_context("display.max_rows", None, "display.max_columns", None)  # type: ignore
def display_df(df: DataFrame | NDFrame | Series, clear: bool = False):
    not clear or clear_output()
    _ = display(df)


def display_dict_as_df(data_display: Dict[Any, Any]):
    display_df(pd.DataFrame.from_records([data_display], index=[""]))


def display_as_df(**kwargs: Any):
    display_df(pd.DataFrame.from_records([kwargs]))


def display_dicts_as_dfs(data_displays: List[Dict[str, Any]]):
    for data_display in data_displays:
        display_dict_as_df(data_display)


def pretty_print_dict(dicty: Dict[str, Any]):
    print(json.dumps(dicty, indent=0,)[1:-1].replace('"', "").replace(",", ""))


def pretty_print(**kwargs: Any):
    pretty_print_dict(kwargs)


def secondsToText(secs: int):
    days = secs // 86400
    hours = (remaining := (secs - days * 86400)) // 3600
    minutes = (remaining := (remaining - hours * 3600)) // 60
    seconds = remaining - minutes * 60
    time_str = ''
    if days:
        time_str += f"{days}d" + ", " if seconds or minutes or hours else ""
    if hours:
        time_str += f"{hours}h" + ", " if seconds or minutes else ""
    if minutes:
        time_str += f"{minutes}m" + ", " if seconds else ""
    if seconds:
        time_str += f"{seconds}s"
    return time_str


def round_hour(ts: int):
    q, r = divmod(ts, 3600)
    return (q + 1 if r >= 1800 else q) * 3600


def round_hour_down(ts: int):
    q, _ = divmod(ts, 3600)
    return q * 3600


def dump_datetime(value: datetime):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]


def convert_keys(json: Any, converter: Callable[[str], str]) -> Any:
    if json is None:
        return
    elif isinstance(json, list):
        return [convert_keys(item, converter=converter) for item in cast(list[Any], json)]
    elif isinstance(json, dict):
        for current_key, value in cast(dict[Any, Any], json).copy().items():
            new_key = converter(current_key) if isinstance(current_key, str) else current_key
            values_needs_converting = isinstance(value, dict) or isinstance(value, list)
            new_value: Any = convert_keys(value, converter=converter) if values_needs_converting else value
            if new_key != current_key:
                json[new_key] = new_value
                del json[current_key]
            else:
                json[current_key] = new_value
    return cast(Any, json)

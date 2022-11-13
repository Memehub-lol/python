from typing import Any, Dict, List, Union

import pandas as pd
from IPython.core.display import clear_output
from IPython.display import display
from pandas import option_context
from pandas.core.frame import DataFrame
from pandas.core.generic import NDFrame
from pandas.core.series import Series


class JupyterDisplay:
    @option_context("display.max_rows", None, "display.max_columns", None)  # type: ignore
    @classmethod
    def display_df(cls, df: Union[DataFrame, NDFrame, Series], clear: bool = False):
        not clear or clear_output()
        _ = display(df)

    @classmethod
    def display_dict_as_df(cls, data_display: Dict[Any, Any]):
        cls.display_df(pd.DataFrame.from_records([data_display], index=[""]))

    @classmethod
    def display_as_df(cls, **kwargs: Any):
        cls.display_df(pd.DataFrame.from_records([kwargs]))

    @classmethod
    def display_dicts_as_dfs(cls, data_displays: List[Dict[str, Any]]):
        for data_display in data_displays:
            cls.display_dict_as_df(data_display)

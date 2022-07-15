

from IPython.core.display import clear_output
from src.lib.utils import display_dict_as_df


def options_input_handler(label: str, options: list[str]) -> str:
    display_dict_as_df({idx: option for idx, option in enumerate(options)})
    keypress = input(label)
    clear_output()
    if keypress not in list(map(str, range(len(options)))):
        print("incorrect input, try again")
        return options_input_handler(label, options)
    return options[int(keypress)]


def int_input_handler(label: str) -> int:
    keypress = input(label)
    clear_output()
    try:
        return int(keypress)
    except ValueError:
        print("incorrect input, try again")
        return int_input_handler(label)

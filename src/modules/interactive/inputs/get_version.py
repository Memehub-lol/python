from src.lib.versioning import Versioner
from src.modules.interactive.inputs.input_handler import options_input_handler


def get_meme_version():
    version_modes = ["lts", "edge", "manual"]
    version_mode = options_input_handler("Select Meme Version:", version_modes)
    if version_mode == "lts":
        return Versioner.meme_clf(True)
    elif version_mode == "edge":
        return Versioner.meme_clf(False)
    meme_versions = Versioner.all_meme_clf_versions()
    return options_input_handler("Input version, avaliable:", meme_versions)

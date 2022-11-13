from src.enums.e_memeclf_version import EMemeClfVersion
from src.interactive.inputs.input_handler import options_input_handler


def get_meme_version():
    version_modes = ["lts", "edge", "manual"]
    version_mode = options_input_handler("Select Meme Version:", version_modes)
    if version_mode == "lts":
        return EMemeClfVersion.get_version_by_lts(True)
    elif version_mode == "edge":
        return EMemeClfVersion.get_version_by_lts(False)
    meme_versions = EMemeClfVersion.all_meme_clf_versions()
    return options_input_handler("Input version, avaliable:", meme_versions)

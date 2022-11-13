from typing import Any

from src.modules.interactive.components.bootstrap.prediction_bootstrapper import \
    PredictionBootstrapper
from src.modules.interactive.components.meme_clf_auditor import \
    IPyMemeClfAuditor
from src.modules.interactive.inputs.input_handler import options_input_handler

registry: list[Any] = [IPyMemeClfAuditor, PredictionBootstrapper]
registry_names = [item.__name__ for item in registry]
registry_name_class_dict = dict(zip(registry_names, registry))

label = ("Welcome to the Memehub Ai Interactive System.\n" +
         "Please select a component to load by number.\n" +
         "Components:\n")


def entry_point() -> None:
    registry_name = options_input_handler(label, registry_names)
    return registry_name_class_dict[registry_name].entry_point()

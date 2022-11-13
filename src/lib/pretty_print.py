import json
from typing import Any, Dict


class PrettyPrint:
    @classmethod
    def dict(cls, dicty: Dict[str, Any]):
        print(json.dumps(dicty, indent=0,)[1:-1].replace('"', "").replace(",", ""))

    @classmethod
    def kwargs(cls, **kwargs: Any):
        cls.dict(kwargs)

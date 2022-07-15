from typing import Any, Protocol


class IPyProtocol:
    @classmethod
    def entry_point(cls) -> None:
        raise NotImplementedError()

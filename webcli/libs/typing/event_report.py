from dataclasses import dataclass
from typing import Any


@dataclass
class ProcessCaller:
    name: str
    kwargs: dict[str, Any]

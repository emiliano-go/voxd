from dataclasses import dataclass
from collections.abc import Callable


@dataclass(frozen=True)
class Ok:
    tool: str
    detail: str = ""


@dataclass(frozen=True)
class Rejected:
    tool: str | None
    reason: str
    kind: str                 # unknown_tool | bad_args | invalid_value | declined


@dataclass(frozen=True)
class Failed:
    tool: str
    reason: str


Result = Ok | Rejected | Failed


@dataclass(frozen=True)
class ParamSpec:
    required: bool
    enum: frozenset[str] | None = None
    coerce: Callable[[str], str] | None = None


@dataclass(frozen=True)
class Entry:
    fn: Callable[..., Result]
    description: str
    params: dict[str, ParamSpec]

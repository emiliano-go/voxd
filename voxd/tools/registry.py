from dataclasses import dataclass
from collections.abc import Callable

from volume import volume_control


@dataclass(frozen=True)
class Ok:
    tool: str
    detail: str = ""          # "launched firefox", for the popup/log


@dataclass(frozen=True)
class Rejected:
    tool: str | None
    reason: str               # why it was refused, pre-execution
    kind: str                 # unknown_tool | bad_args | invalid_value | declined


@dataclass(frozen=True)
class Failed:
    tool: str
    reason: str               # handler ran and blew up (binary missing, etc.)


Result = Ok | Rejected | Failed


@dataclass(frozen=True)
class ParamSpec:
    required: bool
    enum: frozenset[str] | None = None
    coerce: Callable[[str], str] | None = None


@dataclass(frozen=True)
class Entry:
    fn: Callable[..., Result]
    description: str                    # what Needle sees in the tool schema
    params: dict[str, ParamSpec]        # what validate() enforces


# Tool registry
REGISTRY: dict[str, Entry] = {
    "volume_control" : volume_control,
}


# Handler Registration
def register(name : str, *, description : str, params : dict[str, ParamSpec]):
    
    def decorator(fn):
        
        if name in REGISTRY:
            raise ValueError(f"duplicate tool name: {name}")  # catch typo'd duplicate names at import
        
        REGISTRY[name] = Entry(fn=fn, description=description, params=params)
        
        return fn                    # unchanged, fn stays directly callable/testable
    
    return decorator


def dispatch(call):
    fn = REGISTRY.get(call["name"])
    if fn is None:
        return f"rejected: unknown tool {call['name']}"
    return fn(**call["arguments"])
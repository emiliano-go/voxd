from .types import Ok, Rejected, Failed, Result, ParamSpec, Entry
from .system_query import system_query
from .volume import volume_control
from .media import media_control
from .apps import launch_app
from .window import window_action
from .workspace import workspace_switch


REGISTRY: dict[str, Entry] = {
    "system_query": Entry(
        fn=system_query,
        description="Check system status.",
        params={
            "query": ParamSpec(
                required=True,
                enum=frozenset({"battery", "time", "network", "disk"}),
            ),
        },
    ),
    "volume_control": Entry(
        fn=volume_control,
        description="Change or mute system audio volume.",
        params={
            "action": ParamSpec(
                required=True,
                enum=frozenset({"up", "down", "mute", "set"}),
            ),
            "amount": ParamSpec(required=False),
        },
    ),
    "media_control": Entry(
        fn=media_control,
        description="Control media playback.",
        params={
            "action": ParamSpec(
                required=True,
                enum=frozenset({"play", "pause", "next", "previous"}),
            ),
        },
    ),
    "launch_app": Entry(
        fn=launch_app,
        description="Launch, open, or start an application that is not running yet.",
        params={
            "app": ParamSpec(required=True),
        },
    ),
    "window_action": Entry(
        fn=window_action,
        description=(
            "Act on an already-open window: close it, focus it, or make it "
            "fullscreen. Also used to quit or kill a running application."
        ),
        params={
            "action": ParamSpec(
                required=True,
                enum=frozenset({"close", "focus", "fullscreen"}),
            ),
            "target": ParamSpec(required=False),
        },
    ),
    "workspace_switch": Entry(
        fn=workspace_switch,
        description="Switch to a different workspace by number.",
        params={
            "workspace": ParamSpec(required=True),
        },
    ),
}


def known_tools() -> list[dict]:
    tools = []
    for name, entry in REGISTRY.items():
        params = {}
        for pname, pspec in entry.params.items():
            param: dict = {"type": "string", "required": pspec.required}
            if pspec.enum:
                param["description"] = f"Exactly one of: {', '.join(sorted(pspec.enum))}"
                param["enum"] = sorted(pspec.enum)
            else:
                param["description"] = pname
            params[pname] = param
        tools.append({"name": name, "description": entry.description, "parameters": params})
    return tools


def validate(name: str, args: dict, params: dict[str, ParamSpec]) -> dict | Rejected:
    cleaned: dict[str, str] = {}
    for param, spec in params.items():
        value = args.get(param)
        if value is None:
            if spec.required:
                return Rejected(name, f"missing required argument {param!r}", "bad_args")
            continue
        if spec.enum is not None and value not in spec.enum:
            return Rejected(
                name,
                f"invalid value {value!r} for {param!r}; "
                f"must be one of {sorted(spec.enum)}",
                "invalid_value",
            )
        if spec.coerce:
            value = spec.coerce(value)
        cleaned[param] = value
    return cleaned


def dispatch(call) -> Result:
    if not call:
        return Rejected(None, "no tool call", "declined")
    name = call.get("name")
    entry = REGISTRY.get(name)
    if entry is None:
        return Rejected(name, f"unknown tool {name!r}", "unknown_tool")
    args = call.get("arguments", {})
    cleaned = validate(name, args, entry.params)
    if isinstance(cleaned, Rejected):
        return cleaned
    try:
        return entry.fn(**cleaned)
    except Exception as e:
        return Failed(name, str(e))

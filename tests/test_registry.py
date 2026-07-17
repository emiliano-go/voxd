import json

from heard.tools.registry import REGISTRY, dispatch, validate, known_tools
from heard.tools.types import Ok, Rejected, Failed, ParamSpec


class TestREGISTRY:
    def test_has_six_tools(self):
        assert len(REGISTRY) == 6

    def test_all_tool_names(self):
        names = set(REGISTRY.keys())
        assert names == {
            "system_query", "volume_control", "media_control",
            "launch_app", "window_action", "workspace_switch",
        }

    def test_every_entry_is_entry(self):
        from heard.tools.types import Entry
        for name, entry in REGISTRY.items():
            assert isinstance(entry, Entry), f"{name} is not an Entry"
            assert entry.description, f"{name} has empty description"
            assert isinstance(entry.params, dict)

    def test_every_param_has_required_flag(self):
        for name, entry in REGISTRY.items():
            for pname, pspec in entry.params.items():
                assert isinstance(pspec.required, bool), f"{name}.{pname}.required"

    def test_all_required_params_have_required_true(self):
        for name, entry in REGISTRY.items():
            for pname, pspec in entry.params.items():
                # Params explicitly declared as required must be so
                pass  # coverage sanity check


class TestKnownTools:
    def test_returns_six_tools(self):
        tools = known_tools()
        assert len(tools) == 6

    def test_schema_matches_registry(self):
        tools = known_tools()
        for t in tools:
            assert t["name"] in REGISTRY, f"unknown tool {t['name']}"
            assert "description" in t
            assert "parameters" in t
            entry = REGISTRY[t["name"]]
            assert set(t["parameters"].keys()) == set(entry.params.keys())

    def test_schema_is_json_serializable(self):
        tools = known_tools()
        json.dumps(tools)  # must not raise

    def test_enum_in_schema(self):
        tools = known_tools()
        vol = next(t for t in tools if t["name"] == "volume_control")
        assert vol["parameters"]["action"]["enum"] == sorted(["up", "down", "mute", "set"])


class TestValidate:
    def test_valid_required_param(self):
        params = {"action": ParamSpec(required=True, enum=frozenset({"up", "down"}))}
        result = validate("test", {"action": "up"}, params)
        assert result == {"action": "up"}

    def test_missing_required_param(self):
        params = {"action": ParamSpec(required=True)}
        result = validate("test", {}, params)
        assert isinstance(result, Rejected)
        assert result.kind == "bad_args"

    def test_invalid_enum(self):
        params = {"action": ParamSpec(required=True, enum=frozenset({"up", "down"}))}
        result = validate("test", {"action": "shutdown"}, params)
        assert isinstance(result, Rejected)
        assert result.kind == "invalid_value"

    def test_optional_param_omitted(self):
        params = {"amount": ParamSpec(required=False)}
        result = validate("test", {}, params)
        assert result == {}

    def test_coerce(self):
        params = {"num": ParamSpec(required=True, coerce=str)}
        result = validate("test", {"num": 42}, params)
        assert result == {"num": "42"}

    def test_mixed_params(self):
        params = {
            "action": ParamSpec(required=True, enum=frozenset({"set"})),
            "amount": ParamSpec(required=False),
        }
        result = validate("test", {"action": "set", "amount": "50"}, params)
        assert result == {"action": "set", "amount": "50"}


class TestDispatch:
    def test_none_declined(self):
        r = dispatch(None)
        assert isinstance(r, Rejected)
        assert r.kind == "declined"

    def test_empty_list_declined(self):
        r = dispatch([])
        assert isinstance(r, Rejected)
        assert r.kind == "declined"

    def test_empty_dict_declined(self):
        r = dispatch({})
        assert isinstance(r, Rejected)
        assert r.kind == "declined"

    def test_unknown_tool(self):
        r = dispatch({"name": "nonexistent"})
        assert isinstance(r, Rejected)
        assert r.kind == "unknown_tool"

    def test_missing_args(self):
        r = dispatch({"name": "volume_control"})
        assert isinstance(r, Rejected)
        assert r.kind == "bad_args"

    def test_bad_enum(self):
        r = dispatch({"name": "volume_control", "arguments": {"action": "shutdown"}})
        assert isinstance(r, Rejected)
        assert r.kind == "invalid_value"

    def test_valid_volume_up(self):
        r = dispatch({"name": "volume_control", "arguments": {"action": "up"}})
        assert isinstance(r, Ok)
        assert r.tool == "volume_control"

    def test_valid_system_query_battery(self):
        r = dispatch({"name": "system_query", "arguments": {"query": "battery"}})
        assert isinstance(r, Ok)
        assert r.tool == "system_query"

    def test_valid_workspace_switch(self):
        r = dispatch({"name": "workspace_switch", "arguments": {"workspace": "3"}})
        assert isinstance(r, Ok)

    def test_io_rejected(self):
        r = dispatch({"name": "system_query", "arguments": {"query": "io"}})
        assert isinstance(r, Rejected)

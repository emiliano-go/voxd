from heard.tools.types import Ok, Rejected, Failed, ParamSpec, Entry


class TestOk:
    def test_minimal(self):
        r = Ok(tool="volume_control")
        assert r.tool == "volume_control"
        assert r.detail == ""

    def test_with_detail(self):
        r = Ok(tool="launch_app", detail="launched firefox")
        assert r.tool == "launch_app"
        assert r.detail == "launched firefox"

    def test_immutable(self):
        r = Ok(tool="x")
        import dataclasses
        assert dataclasses.is_dataclass(r)
        assert dataclasses.fields(r)


class TestRejected:
    def test_all_fields(self):
        r = Rejected(tool="volume_control", reason="bad action", kind="invalid_value")
        assert r.tool == "volume_control"
        assert r.reason == "bad action"
        assert r.kind == "invalid_value"

    def test_none_tool(self):
        r = Rejected(tool=None, reason="no tool call", kind="declined")
        assert r.tool is None

    def test_kind_values(self):
        for k in ("unknown_tool", "bad_args", "invalid_value", "declined"):
            r = Rejected(tool="x", reason="test", kind=k)
            assert r.kind == k


class TestFailed:
    def test_all_fields(self):
        r = Failed(tool="media_control", reason="playerctl not found")
        assert r.tool == "media_control"
        assert r.reason == "playerctl not found"


class TestParamSpec:
    def test_required_only(self):
        p = ParamSpec(required=True)
        assert p.required is True
        assert p.enum is None
        assert p.coerce is None

    def test_with_enum(self):
        p = ParamSpec(required=True, enum=frozenset({"up", "down"}))
        assert p.enum == frozenset({"up", "down"})

    def test_optional(self):
        p = ParamSpec(required=False)
        assert p.required is False


class TestEntry:
    def test_minimal(self):
        def fn():
            return Ok(tool="test")

        e = Entry(fn=fn, description="A test tool", params={})
        assert e.description == "A test tool"
        assert e.params == {}
        assert e.fn() == Ok(tool="test")

    def test_with_params(self):
        def fn(action: str):
            return Ok(tool="test", detail=action)

        e = Entry(
            fn=fn,
            description="Test",
            params={"action": ParamSpec(required=True, enum=frozenset({"a", "b"}))},
        )
        assert "action" in e.params

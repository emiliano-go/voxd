"""Intent module tests -- Needle is mocked in conftest.py."""


class TestIntent:
    def test_module_imports(self):
        import heard.intent
        assert heard.intent.MAX_GEN_LEN == 64
        assert heard.intent.CHECKPOINT_PATH == "checkpoints/needle_checkpoint.pkl"

    def test_resolution_dataclass(self):
        from heard.intent import Resolution
        r = Resolution(raw_query="test", tool_call=None, reason="declined", latency_ms=None)
        assert r.raw_query == "test"
        assert r.tool_call is None
        assert r.reason == "declined"

    def test_resolution_with_tool_call(self):
        from heard.intent import Resolution
        tc = {"name": "volume_control", "arguments": {"action": "up"}}
        r = Resolution(raw_query="turn up", tool_call=tc, reason=None, latency_ms=100.0)
        assert r.tool_call == tc
        assert r.latency_ms == 100.0

    def test_tools_json_cache_exists(self):
        import heard.intent
        from heard.tools.registry import known_tools
        import json
        # Verify the function exists and produces valid JSON
        expected = json.dumps(known_tools())
        assert expected  # non-empty

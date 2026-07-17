"""STT module tests -- all hardware access is mocked in conftest.py."""


class TestSTT:
    def test_module_imports(self):
        import heard.stt
        assert heard.stt.SAMPLE_RATE == 16000

    def test_keycode(self):
        from heard.stt import _keycode
        assert _keycode("KEY_LEFTSHIFT") == 42
        assert _keycode("KEY_LEFTCONTROL") == 29

    def test_keycode_invalid(self):
        from heard.stt import _keycode
        try:
            _keycode("KEY_NONEXISTENT")
            assert False, "expected ValueError"
        except ValueError:
            pass

    def test_find_input_device_no_devices(self):
        from heard.stt import _find_input_device
        try:
            _find_input_device()
            assert False, "expected RuntimeError"
        except RuntimeError as e:
            assert "input" in str(e).lower() or "usermod" in str(e)

from unittest import mock

from heard.tools.window import window_action
from heard.tools.types import Ok, Rejected, Failed


class TestWindowAction:
    @mock.patch("heard.tools.window.subprocess.run")
    def test_close(self, mock_run):
        r = window_action("close")
        assert isinstance(r, Ok)
        mock_run.assert_called_once()

    @mock.patch("heard.tools.window.subprocess.run")
    def test_fullscreen(self, mock_run):
        r = window_action("fullscreen")
        assert isinstance(r, Ok)
        mock_run.assert_called_once()

    @mock.patch("heard.tools.window.subprocess.run")
    def test_focus(self, mock_run):
        r = window_action("focus", target="firefox")
        assert isinstance(r, Ok)
        mock_run.assert_called_once()

    def test_focus_no_target(self):
        r = window_action("focus")
        assert isinstance(r, Rejected)
        assert r.kind == "bad_args"

    def test_bad_action(self):
        r = window_action("shutdown")
        assert isinstance(r, Rejected)
        assert r.kind == "invalid_value"

    @mock.patch("heard.tools.window.subprocess.run", side_effect=FileNotFoundError("hyprctl"))
    def test_missing_hyprctl(self, mock_run):
        r = window_action("close")
        assert isinstance(r, Failed)

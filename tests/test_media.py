from unittest import mock

from heard.tools.media import media_control
from heard.tools.types import Ok, Rejected, Failed


class TestMediaControl:
    @mock.patch("heard.tools.media.subprocess.run")
    def test_play(self, mock_run):
        r = media_control("play")
        assert isinstance(r, Ok)
        mock_run.assert_called_once()

    @mock.patch("heard.tools.media.subprocess.run")
    def test_pause(self, mock_run):
        r = media_control("pause")
        assert isinstance(r, Ok)
        mock_run.assert_called_once()

    @mock.patch("heard.tools.media.subprocess.run")
    def test_next(self, mock_run):
        r = media_control("next")
        assert isinstance(r, Ok)
        mock_run.assert_called_once()

    @mock.patch("heard.tools.media.subprocess.run")
    def test_previous(self, mock_run):
        r = media_control("previous")
        assert isinstance(r, Ok)
        mock_run.assert_called_once()

    def test_bad_action(self):
        r = media_control("shutdown")
        assert isinstance(r, Rejected)
        assert r.kind == "invalid_value"

    @mock.patch("heard.tools.media.subprocess.run", side_effect=FileNotFoundError("playerctl"))
    def test_missing_playerctl(self, mock_run):
        r = media_control("play")
        assert isinstance(r, Failed)

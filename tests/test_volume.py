from unittest import mock

from heard.tools.volume import volume_control
from heard.tools.types import Ok, Rejected, Failed


class TestVolumeControl:
    @mock.patch("heard.tools.volume.subprocess.run")
    def test_up(self, mock_run):
        r = volume_control("up")
        assert isinstance(r, Ok)
        mock_run.assert_called_once()

    @mock.patch("heard.tools.volume.subprocess.run")
    def test_down(self, mock_run):
        r = volume_control("down")
        assert isinstance(r, Ok)
        mock_run.assert_called_once()

    @mock.patch("heard.tools.volume.subprocess.run")
    def test_mute(self, mock_run):
        r = volume_control("mute")
        assert isinstance(r, Ok)
        mock_run.assert_called_once()

    @mock.patch("heard.tools.volume.subprocess.run")
    def test_set(self, mock_run):
        r = volume_control("set", amount="50")
        assert isinstance(r, Ok)
        mock_run.assert_called_once()

    def test_set_missing_amount(self):
        r = volume_control("set")
        assert isinstance(r, Rejected)
        assert r.kind == "bad_args"

    def test_bad_action(self):
        r = volume_control("shutdown")
        assert isinstance(r, Rejected)
        assert r.kind == "invalid_value"

    @mock.patch("heard.tools.volume.subprocess.run", side_effect=FileNotFoundError("wpctl"))
    def test_missing_wpctl(self, mock_run):
        r = volume_control("up")
        assert isinstance(r, Failed)

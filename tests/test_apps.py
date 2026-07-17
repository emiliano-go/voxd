from unittest import mock

from heard.tools.apps import launch_app
from heard.tools.types import Ok, Rejected, Failed


class TestLaunchApp:
    @mock.patch("heard.tools.apps.app_exists", return_value=True)
    @mock.patch("heard.tools.apps.subprocess.Popen")
    def test_launch(self, mock_popen, mock_exists):
        r = launch_app("firefox")
        assert isinstance(r, Ok)
        mock_popen.assert_called_once()

    @mock.patch("heard.tools.apps.app_exists", return_value=False)
    def test_app_not_found(self, mock_exists):
        r = launch_app("nonexistent")
        assert isinstance(r, Rejected)
        assert r.kind == "declined"

    @mock.patch("heard.tools.apps.app_exists", return_value=True)
    @mock.patch("heard.tools.apps.subprocess.Popen", side_effect=FileNotFoundError("uwsm"))
    def test_missing_uwsm(self, mock_popen, mock_exists):
        r = launch_app("firefox")
        assert isinstance(r, Rejected)
        assert r.kind == "declined"

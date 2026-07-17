from unittest import mock

from heard.tools.helpers.apps import app_exists


class TestAppExists:
    @mock.patch("heard.tools.helpers.apps.shutil.which", return_value="/usr/bin/firefox")
    def test_found(self, mock_which):
        assert app_exists("firefox") is True
        mock_which.assert_called_once_with("firefox")

    @mock.patch("heard.tools.helpers.apps.shutil.which", return_value=None)
    def test_not_found(self, mock_which):
        assert app_exists("nonexistent") is False

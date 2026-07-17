from unittest import mock

from heard.tools.workspace import workspace_switch
from heard.tools.types import Ok, Rejected, Failed


class TestWorkspaceSwitch:
    @mock.patch("heard.tools.workspace.subprocess.run")
    def test_valid(self, mock_run):
        r = workspace_switch("3")
        assert isinstance(r, Ok)
        mock_run.assert_called_once()

    @mock.patch("heard.tools.workspace.subprocess.run")
    def test_valid_min(self, mock_run):
        r = workspace_switch("1")
        assert isinstance(r, Ok)

    @mock.patch("heard.tools.workspace.subprocess.run")
    def test_valid_max(self, mock_run):
        r = workspace_switch("10")
        assert isinstance(r, Ok)

    def test_out_of_range_above(self):
        r = workspace_switch("99")
        assert isinstance(r, Rejected)
        assert r.kind == "invalid_value"

    def test_out_of_range_below(self):
        r = workspace_switch("0")
        assert isinstance(r, Rejected)
        assert r.kind == "invalid_value"

    def test_not_a_number(self):
        r = workspace_switch("abc")
        assert isinstance(r, Rejected)
        assert r.kind == "invalid_value"

    @mock.patch("heard.tools.workspace.subprocess.run", side_effect=FileNotFoundError("hyprctl"))
    def test_missing_hyprctl(self, mock_run):
        r = workspace_switch("3")
        assert isinstance(r, Failed)

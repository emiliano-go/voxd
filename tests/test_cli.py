from typer.testing import CliRunner

from heard.cli import app

runner = CliRunner()


class TestCLI:
    def test_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "listen" in result.output
        assert "config" in result.output

    def test_listen_help(self):
        result = runner.invoke(app, ["listen", "--help"])
        assert result.exit_code == 0
        assert "hold the PTT key" in result.output

    def test_config_help(self):
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "get" in result.output
        assert "set" in result.output
        assert "show" in result.output

    def test_config_get(self):
        result = runner.invoke(app, ["config", "get", "wm.backend"])
        assert result.exit_code == 0
        assert "wm.backend" in result.output

    def test_config_set(self):
        result = runner.invoke(app, ["config", "set", "wm.backend", "hyprland"])
        assert result.exit_code == 0
        assert "wm.backend" in result.output

    def test_config_show(self):
        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0

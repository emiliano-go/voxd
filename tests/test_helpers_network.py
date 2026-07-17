from unittest import mock
from pathlib import Path

from heard.tools.helpers.network import (
    _has_active_interface,
    _has_internet,
    NetworkState,
)


class TestNetworkState:
    def test_enum_values(self):
        assert NetworkState.CONNECTED.value == "connected"
        assert NetworkState.LIMITED.value == "limited"
        assert NetworkState.DISCONNECTED.value == "disconnected"


class TestHasActiveInterface:
    @mock.patch("heard.tools.helpers.network.Path.iterdir")
    def test_loopback_only(self, mock_iterdir):
        mock_iterdir.return_value = [Path("/sys/class/net/lo")]
        assert _has_active_interface() is False

    @mock.patch("heard.tools.helpers.network.Path.iterdir")
    def test_wifi_up(self, mock_iterdir):
        wifi = Path("/sys/class/net/wlan0")
        operstate = wifi / "operstate"
        mock_iterdir.return_value = [Path("/sys/class/net/lo"), wifi]

        with mock.patch.object(Path, "iterdir", return_value=[Path("/sys/class/net/lo"), wifi]):
            with mock.patch.object(Path, "read_text", return_value="up"):
                assert _has_active_interface() is True

    @mock.patch("heard.tools.helpers.network.Path.iterdir")
    def test_interface_down(self, mock_iterdir):
        eth = Path("/sys/class/net/eth0")
        with mock.patch.object(Path, "iterdir", return_value=[Path("/sys/class/net/lo"), eth]):
            with mock.patch.object(Path, "read_text", return_value="down"):
                assert _has_active_interface() is False

    @mock.patch("heard.tools.helpers.network.Path.iterdir")
    def test_oserror_on_read(self, mock_iterdir):
        eth = Path("/sys/class/net/eth0")
        with mock.patch.object(Path, "iterdir", return_value=[Path("/sys/class/net/lo"), eth]):
            with mock.patch.object(Path, "read_text", side_effect=OSError):
                assert _has_active_interface() is False


class TestHasInternet:
    @mock.patch("heard.tools.helpers.network.socket.create_connection")
    def test_internet_reachable(self, mock_conn):
        assert _has_internet() is True

    @mock.patch("heard.tools.helpers.network.socket.create_connection", side_effect=OSError)
    def test_no_internet_first_endpoint(self, mock_conn):
        assert _has_internet() is False

    @mock.patch("heard.tools.helpers.network.socket.create_connection")
    def test_fallback_endpoint(self, mock_conn):
        """First fails, second succeeds."""
        mock_conn.side_effect = [OSError, mock.MagicMock()]
        assert _has_internet() is True

    @mock.patch("heard.tools.helpers.network.socket.create_connection", side_effect=OSError)
    def test_all_endpoints_fail(self, mock_conn):
        assert _has_internet() is False
        assert mock_conn.call_count == 2

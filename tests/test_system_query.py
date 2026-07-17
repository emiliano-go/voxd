from unittest import mock

from heard.tools.system_query import system_query
from heard.tools.types import Ok, Rejected, Failed


class TestSystemQuery:
    def test_battery(self):
        r = system_query("battery")
        assert isinstance(r, (Ok, Failed))
        # May fail in CI with no battery, but that's a Failed, not crash

    def test_time(self):
        r = system_query("time")
        assert isinstance(r, Ok)
        assert isinstance(r.detail, str)

    def test_network(self):
        with mock.patch("heard.tools.system_query._has_active_interface", return_value=False):
            r = system_query("network")
            assert isinstance(r, Ok)  # returns disconnected state as Ok
            assert "DISCONNECTED" in r.detail

    def test_disk(self):
        r = system_query("disk")
        assert isinstance(r, Ok)
        assert "total" in r.detail
        assert "used" in r.detail

    def test_unknown_query(self):
        r = system_query("nonexistent")
        assert isinstance(r, Rejected)
        assert r.kind == "invalid_value"

    def test_internal_battery_private(self):
        from heard.tools.system_query import _battery
        result = _battery()
        # Returns tuple or None (no battery in some environments)
        assert result is None or (isinstance(result, tuple) and len(result) == 2)

    def test_internal_disk_private(self):
        from heard.tools.system_query import _disk
        result = _disk()
        assert isinstance(result, dict)
        assert "total" in result

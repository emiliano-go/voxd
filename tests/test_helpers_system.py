import pytest

from heard.tools.helpers.system import format_bytes, is_physical_disk


class TestFormatBytes:
    @pytest.mark.parametrize("n,expected", [
        (0, "0.0 B"),
        (1, "1.0 B"),
        (512, "512.0 B"),
        (1023, "1023.0 B"),
        (1024, "1.0 KiB"),
        (1536, "1.5 KiB"),
        (1048576, "1.0 MiB"),
        (1073741824, "1.0 GiB"),
        (1099511627776, "1.0 TiB"),
        (2 ** 40 * 1.5, "1.5 TiB"),
    ])
    def test_values(self, n, expected):
        assert format_bytes(n) == expected


class TestIsPhysicalDisk:
    @pytest.mark.parametrize("device,expected", [
        ("sda", True),
        ("sdb", True),
        ("sda1", False),       # partition
        ("nvme0n1", True),
        ("nvme0n1p1", False),  # partition
        ("mmcblk0", True),
        ("vda", True),
        ("xvdh", True),
        ("loop0", False),
        ("dm-0", False),
        ("zram0", False),
        ("", False),
    ])
    def test_matches(self, device, expected):
        assert is_physical_disk(device) is expected

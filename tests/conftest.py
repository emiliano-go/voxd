"""Shared fixtures and mocks for all tests.

Heavy modules (evdev, sounddevice, faster_whisper, needle) are mocked
at the module level so importing heard modules doesn't trigger hardware
access or expensive model loads.
"""

import sys
from unittest import mock

# Mock heavy dependencies before any heard import touches them
for mod_name in ("evdev", "sounddevice", "faster_whisper", "needle"):
    sys.modules[mod_name] = mock.MagicMock()

# Give ecodes realistic behavior: known keys resolve to ints, unknown raise
ecodes = mock.Mock(spec_set=["KEY_LEFTSHIFT", "KEY_LEFTCONTROL", "KEY_ESC"])
ecodes.KEY_LEFTSHIFT = 42
ecodes.KEY_LEFTCONTROL = 29
ecodes.KEY_ESC = 1
sys.modules["evdev"].ecodes = ecodes

# Patch list_devices to return empty (no input devices in CI)
sys.modules["evdev"].list_devices.return_value = []

import functools

import numpy as np
import sounddevice as sd
from evdev import InputDevice, list_devices, ecodes
from faster_whisper import WhisperModel


SAMPLE_RATE = 16000
WHISPER_SIZE = "base"


@functools.lru_cache(maxsize=1)
def _model():
    return WhisperModel(WHISPER_SIZE, device="cpu", compute_type="int8")


def _keycode(key_name: str) -> int:
    try:
        return getattr(ecodes, key_name)
    except AttributeError:
        raise ValueError(
            f"unknown key code {key_name!r}; "
            f"use e.g. KEY_LEFTSHIFT, KEY_LEFTCONTROL, KEY_SCROLLLOCK"
        )


def _find_input_device() -> InputDevice:
    paths = list_devices()
    if not paths:
        raise RuntimeError(
            "No input devices found in /dev/input/.\n"
            "Make sure you are in the 'input' group:\n"
            "  sudo usermod -aG input $USER\n"
            "Then log out and back in."
        )
    for path in paths:
        try:
            dev = InputDevice(path)
            if ecodes.EV_KEY in dev.capabilities():
                return dev
        except PermissionError:
            continue
    raise RuntimeError(
        "No accessible keyboard device found.\n"
        "Make sure you are in the 'input' group:\n"
        "  sudo usermod -aG input $USER\n"
        "Then log out and back in."
    )


def capture_while_held(ptt_key: str = "KEY_LEFTSHIFT") -> str:
    code = _keycode(ptt_key)
    dev = _find_input_device()
    recording = False
    chunks: list[np.ndarray] | None = None
    stream: sd.InputStream | None = None

    for event in dev.read_loop():
        if event.type != ecodes.EV_KEY or event.code != code:
            continue

        if event.value == 1 and not recording:
            recording = True
            chunks = []
            stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32",
                callback=lambda indata, frames, time, status: chunks.append(indata.copy()),
            )
            stream.start()

        elif event.value == 0 and recording:
            recording = False
            if stream is not None:
                stream.stop()
                stream.close()
                stream = None

            if not chunks:
                continue

            audio = np.concatenate(chunks, axis=0).flatten()
            model = _model()
            segments, _ = model.transcribe(audio, SAMPLE_RATE)
            return " ".join(s.text.strip() for s in segments).strip()

    return ""

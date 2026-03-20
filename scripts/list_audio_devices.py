from __future__ import annotations

import sounddevice as sd

try:
    from pvrecorder import PvRecorder
except Exception:
    PvRecorder = None


def main() -> None:
    print("== sounddevice input devices ==")
    devices = sd.query_devices()
    for index, device in enumerate(devices):
        max_input = device.get("max_input_channels", 0)
        if max_input and max_input > 0:
            print(f"[{index}] {device['name']} | input_channels={max_input} | hostapi={device['hostapi']}")

    print()
    print("== pvrecorder devices ==")
    if PvRecorder is None:
        print("pvrecorder not installed")
        return

    for index, name in enumerate(PvRecorder.get_available_devices()):
        print(f"[{index}] {name}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import os
import subprocess
import threading
import time
from dataclasses import dataclass, field

from .config import OverlayConfig, TTSConfig
from .state import OverlayStateManager
from .text import clean_text_for_tts


@dataclass(slots=True)
class MacOSTTS:
    config: TTSConfig
    overlay: OverlayConfig
    _current_proc: subprocess.Popen | None = field(default=None, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _state: OverlayStateManager = field(init=False)

    def __post_init__(self) -> None:
        self._state = OverlayStateManager(self.overlay)

    def clear_stop_flag(self) -> None:
        self._state.clear_stop_flag()

    def request_stop(self) -> None:
        self._state.request_stop()

    def is_stop_requested(self) -> bool:
        return self._state.is_stop_requested()

    def stop_current_speech(self) -> None:
        with self._lock:
            proc = self._current_proc
            if proc is None:
                return
            try:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=0.8)
                    except Exception:
                        proc.kill()
            finally:
                self._current_proc = None

    def speak(self, text: str, clean_markdown: bool = True) -> bool:
        if not text:
            return True

        speak_text = clean_text_for_tts(text) if clean_markdown else text
        if not speak_text.strip():
            return True

        self.clear_stop_flag()
        self.stop_current_speech()

        proc = subprocess.Popen(
            ["say", "-v", self.config.voice, speak_text],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        with self._lock:
            self._current_proc = proc

        while True:
            result = proc.poll()
            if result is not None:
                with self._lock:
                    if self._current_proc is proc:
                        self._current_proc = None
                return True
            if self.is_stop_requested():
                self.stop_current_speech()
                self.clear_stop_flag()
                return False
            time.sleep(0.05)

    def play_sound_async(self, sound_path: str) -> None:
        if not sound_path or not os.path.exists(sound_path):
            return
        subprocess.Popen(["afplay", sound_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

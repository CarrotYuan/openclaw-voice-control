from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .config import WakewordConfig


@dataclass(slots=True)
class PorcupineWakewordEngine:
    config: WakewordConfig
    _porcupine: Any | None = field(default=None, init=False)
    _recorder: Any | None = field(default=None, init=False)

    def start(self) -> None:
        if self._porcupine is not None and self._recorder is not None:
            return

        try:
            import pvporcupine
            from pvrecorder import PvRecorder
        except ImportError as exc:
            raise RuntimeError("Porcupine dependencies are not installed.") from exc

        self._porcupine = pvporcupine.create(
            access_key=self.config.access_key,
            keyword_paths=[str(self.config.keyword_path)],
        )
        self._recorder = PvRecorder(device_index=-1, frame_length=self._porcupine.frame_length)
        self._recorder.start()

    def read(self) -> tuple[list[int], int]:
        if self._porcupine is None or self._recorder is None:
            self.start()
        assert self._porcupine is not None
        assert self._recorder is not None
        pcm = self._recorder.read()
        keyword_index = self._porcupine.process(pcm)
        return pcm, keyword_index

    def close(self) -> None:
        if self._recorder is not None:
            self._recorder.stop()
            self._recorder.delete()
            self._recorder = None
        if self._porcupine is not None:
            self._porcupine.delete()
            self._porcupine = None

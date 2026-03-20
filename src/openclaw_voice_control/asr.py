from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .config import ASRConfig


@dataclass(slots=True)
class FunASRSenseVoice:
    config: ASRConfig
    _model: Any | None = None
    _postprocess: Any | None = field(default=None, init=False)

    def load(self) -> None:
        if self._model is not None:
            return

        try:
            from funasr import AutoModel
            from funasr.utils.postprocess_utils import rich_transcription_postprocess
        except ImportError as exc:
            raise RuntimeError(
                "FunASR ASR dependencies are incomplete. Ensure funasr, torch, and torchaudio are installed before running ASR."
            ) from exc

        model_value = str(self.config.model_path) if self.config.model_path else self.config.model
        vad_model_value = str(self.config.vad_model_path) if self.config.vad_model_path else self.config.vad_model

        self._model = AutoModel(
            model=model_value,
            vad_model=vad_model_value,
            vad_kwargs={"max_single_segment_time": 30000},
            device=self.config.device,
            disable_update=self.config.disable_update,
            disable_pbar=self.config.disable_pbar,
        )
        self._postprocess = rich_transcription_postprocess

    def transcribe(self, wav_path: str) -> str:
        self.load()
        assert self._model is not None
        assert self._postprocess is not None

        result = self._model.generate(
            input=wav_path,
            language=self.config.language,
            use_itn=True,
            batch_size_s=60,
        )
        if not result:
            return ""

        text = result[0].get("text", "")
        return self._postprocess(text).strip()

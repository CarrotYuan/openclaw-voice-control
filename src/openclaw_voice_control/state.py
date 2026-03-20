from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

from .config import OverlayConfig


@dataclass(slots=True)
class OverlayStateManager:
    config: OverlayConfig

    def write(
        self,
        status: str,
        user_text: str = "",
        reply_text: str = "",
        meta_text: str = "",
        auto_hide_ms: int = 4000,
    ) -> None:
        if not self.config.enabled:
            return

        payload = {
            "status": status,
            "user_text": user_text,
            "reply_text": reply_text,
            "meta_text": meta_text,
            "auto_hide_ms": auto_hide_ms,
            "updated_at": time.time(),
        }
        target = self.config.state_file
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = Path(str(target) + ".tmp")
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp_path, target)

    def ensure_idle_state(self, reset: bool = True) -> None:
        if not self.config.enabled:
            return
        self.config.state_file.parent.mkdir(parents=True, exist_ok=True)
        if reset or not self.config.state_file.exists():
            self.write("idle", auto_hide_ms=0)

    def clear_stop_flag(self) -> None:
        try:
            if self.config.stop_flag_file.exists():
                self.config.stop_flag_file.unlink()
        except FileNotFoundError:
            pass

    def request_stop(self) -> None:
        self.config.stop_flag_file.parent.mkdir(parents=True, exist_ok=True)
        self.config.stop_flag_file.write_text(str(time.time()), encoding="utf-8")

    def is_stop_requested(self) -> bool:
        return self.config.stop_flag_file.exists()

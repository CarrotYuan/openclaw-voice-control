from __future__ import annotations

import json
import time
from dataclasses import dataclass

import requests

from .config import OpenClawConfig


@dataclass(slots=True)
class OpenClawClient:
    config: OpenClawConfig

    def ask(self, user_text: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": "application/json",
            "x-openclaw-agent-id": self.config.agent_id,
        }
        payload = {
            "model": self.config.model,
            "user": self.config.user,
            "messages": [{"role": "user", "content": user_text}],
            "stream": False,
        }

        started_at = time.time()
        response = requests.post(
            self.config.base_url,
            headers=headers,
            json=payload,
            timeout=self.config.timeout_seconds,
        )
        response.raise_for_status()
        _ = time.time() - started_at

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError):
            return json.dumps(data, ensure_ascii=False, indent=2)

from __future__ import annotations

import argparse

from .config import load_config
from .service import VoiceControlService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the OpenClaw Voice Control service.")
    parser.add_argument("--config", help="Path to config YAML file.")
    parser.add_argument("--env-file", help="Optional .env file to load before config expansion.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(config_path=args.config, env_path=args.env_file)
    service = VoiceControlService(config)
    service.run()

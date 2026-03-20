# Architecture

## Current Public Rewrite Shape

The public rewrite splits the original monolithic script into modules:

- `config.py`: config and env loading
- `state.py`: overlay state and stop-flag coordination
- `text.py`: markdown cleanup for overlay and TTS
- `openclaw_client.py`: OpenClaw request wrapper
- `tts.py`: macOS `say` integration
- `asr.py`: FunASR / SenseVoice wrapper
- `wakeword.py`: Porcupine wrapper
- `service.py`: orchestration for wake, record, transcribe, reply, and follow-up
- `overlay_app.py`: public overlay UI runtime
- `cli.py`: command-line entrypoint

## Scope Decisions

- target platform: macOS
- default ASR language: `zh`
- ASR provider and language remain configurable for later expansion
- ASR loading now supports local model path priority
- overlay remains a separate concern from the core service runtime
- one-click macOS deploy and uninstall scripts manage both service and overlay launch agents

## Why This Matters

This structure is a better base for:

- a public GitHub repository
- a future OpenClaw plugin package
- a future ClawHub companion skill

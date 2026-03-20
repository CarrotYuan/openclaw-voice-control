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
- background startup now uses a project-owned host app launcher rather than
  `launchd -> shell -> bare python`

## Why This Matters

This structure is a better base for:

- a public GitHub repository
- a future OpenClaw plugin package
- a future ClawHub companion skill

## Background Startup Architecture

The most important macOS-specific architectural decision in this public repository
is the background launch path.

Earlier validation showed that this path was not stable enough as the primary
design:

- `launchd -> shell -> bare python`

The repository now uses this path instead:

- `launchd -> host app -> shell script -> python`

The host app is built at deploy time and installed through the LaunchAgent
templates. This keeps the Python service layer intact while giving the background
startup path a more stable macOS process identity.

Implemented files:

- `scripts/openclaw_host_launcher.m`
- `scripts/build_host_apps.sh`
- `launchagents/ai.openclaw.voice-control.plist`
- `launchagents/ai.openclaw.overlay.plist`
- `scripts/deploy_macos.sh`

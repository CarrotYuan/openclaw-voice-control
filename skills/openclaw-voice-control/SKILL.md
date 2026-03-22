# OpenClaw Voice Control

OpenClaw Voice Control is a local macOS voice-control integration for OpenClaw.

It provides:

- wakeword activation
- local microphone capture
- local ASR with FunASR / SenseVoice
- forwarding recognized text to a local OpenClaw agent
- macOS TTS playback
- optional overlay UI
- launchd-based background resident behavior
- auto-start after user login

## Platform

- macOS only

## What This Skill Is

This is not a prompt-only skill and not a small single-function helper.

It should be understood as a local voice entrypoint layer for OpenClaw on macOS.
In practical terms, it gives OpenClaw a Siri-like wakeword-triggered voice
interface on the local machine.

## What This Skill Does Not Bundle

This skill does not bundle:

- `.env`
- a real `.ppn` wakeword file
- OpenClaw tokens
- SenseVoice model files
- VAD model files
- a private OpenClaw runtime

That means installation still requires user-provided local assets and secrets.

## Required User-Provided Items

Before this skill can run, the user must prepare:

- Python 3.11 or newer
- a running local OpenClaw service
- `OPENCLAW_TOKEN`
- `PICOVOICE_ACCESS_KEY`
- a real local `.ppn` wakeword file
- a local SenseVoice model directory
- a local VAD model directory
- macOS microphone permission

## Recommended Defaults

The public repository already provides usable defaults for the OpenClaw target:

- `OPENCLAW_AGENT_ID=main`
- `OPENCLAW_MODEL=openclaw:main`
- `OPENCLAW_USER=openclaw-voice-control`

Users can start with those values and customize later.

## Installation Overview

Read [README.md](../../README.md) first.

`README.md` is the primary installation guide for this project.
[README.zh-CN.md](../../README.zh-CN.md) is the Chinese companion guide.

## Direct Install Path

If an AI or user needs the shortest usable install path, use this sequence:

1. clone the repository
2. create and activate `.venv`
3. install dependencies with `pip install -e .`
4. copy `.env.example` to `.env`
5. fill the required variables in `.env`
6. place the real wakeword file and model directories at the configured paths
7. run foreground validation
8. deploy background resident runtime with `./scripts/deploy_macos.sh`

Minimum command path:

```bash
git clone <repo-url>
cd openclaw-voice-control
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
# fill .env with real values and local asset paths
python -m openclaw_voice_control --config config/default.yaml --env-file .env
./scripts/deploy_macos.sh
```

The normal setup flow is:

1. clone the repository
2. create `.venv`
3. install dependencies
4. copy `.env.example` to `.env`
5. supply real local assets and secrets
6. run foreground validation
7. deploy background runtime with `./scripts/deploy_macos.sh`

For detailed steps, troubleshooting, and validation, use:

- [README.md](../../README.md)
- [README.zh-CN.md](../../README.zh-CN.md)
- [docs/macos-install.md](../../docs/macos-install.md)
- [docs/fresh-clone-validation.md](../../docs/fresh-clone-validation.md)

## Daily Maintenance

For day-to-day use and maintenance, the primary scripts are:

- deploy background runtime: `./scripts/deploy_macos.sh`
- restart installed background services: `./scripts/restart_service.sh`
- uninstall installed background services: `./scripts/uninstall_macos.sh`
- inspect local installation and environment issues: `./scripts/doctor.sh`

Double-click `.command` wrappers are also available in `scripts/` for macOS users who prefer Finder-based execution.

## Background Architecture

The canonical background startup path for this skill is:

- `launchd -> host app -> shell script -> python`

`./scripts/deploy_macos.sh` builds the required host apps automatically.

## Configuration Surface

Important configuration values:

- `OPENCLAW_BASE_URL`
- `OPENCLAW_TOKEN`
- `OPENCLAW_AGENT_ID`
- `OPENCLAW_MODEL`
- `OPENCLAW_USER`
- `PICOVOICE_ACCESS_KEY`
- `WAKEWORD_FILE`
- `SENSEVOICE_MODEL_PATH`
- `SENSEVOICE_VAD_MODEL_PATH`

The interpreter override variables still exist:

- `VOICE_CONTROL_PYTHON_BIN`
- `VOICE_CONTROL_OVERLAY_PYTHON_BIN`

But they are troubleshooting knobs only, not the main deployment model.

## Where To Get Missing Requirements

If a user or another AI is missing required values, files, or local assets, do
not guess.

Read these sections in [README.md](../../README.md):

- `What You Must Prepare Yourself`
- `Required Variables`
- `Where To Get Each Requirement`

Those sections already explain:

- which items must be prepared locally
- where tokens and keys come from
- where the wakeword file and model directories should be placed
- which values belong in `.env`
- how to validate the install before background deployment

Practical source notes:

- `OPENCLAW_TOKEN`: obtain it from the local OpenClaw gateway configuration, such as `openclaw.json-gateway`
- `PICOVOICE_ACCESS_KEY`: obtain it from [Picovoice](https://picovoice.ai/)
- local `.ppn` wakeword file: create and download it from [Picovoice](https://picovoice.ai/)

Important wakeword reminder:

- when training or testing the wakeword on the Picovoice site, make sure the test page clearly shows that the wakeword was triggered successfully
- if the wakeword does not trigger successfully there, local wakeword response may also fail later

## Safety Warning

This skill adds a voice entrypoint, and that entrypoint is not identity-bound.

That means:

- anyone near the microphone may be able to trigger it
- any capability exposed through the connected OpenClaw agent may become
  reachable by voice

Recommended safety practice:

- add explicit safety constraints to the connected agent prompt
- require confirmation for high-risk actions
- avoid broad autonomous permissions for the voice-facing agent
- use least privilege for tools and connected systems

## Related Files

- [skill.json](../../skill.json)
- [docs/openclaw-skill.md](../../docs/openclaw-skill.md)

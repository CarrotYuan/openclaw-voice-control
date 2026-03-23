---
name: openclaw-voice-control
description: Local macOS voice-control integration for OpenClaw. Use when setting up, deploying, troubleshooting, or operating wakeword-triggered voice access to a local OpenClaw agent with ASR, TTS, overlay UI, and launchd background support.
---

# OpenClaw Voice Control

OpenClaw Voice Control is a local macOS voice-control integration for OpenClaw.

Repository source:

- GitHub: [CarrotYuan/openclaw-voice-control](https://github.com/CarrotYuan/openclaw-voice-control)

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
In practical terms, it gives OpenClaw a wakeword-triggered local voice
interface on the local machine.

## What This Skill Does Not Bundle

This skill does not bundle:

- `.env`
- a real `.ppn` wakeword file
- OpenClaw tokens
- SenseVoice model files
- VAD model files
- a private OpenClaw runtime

That means installation still requires user-provided secrets and a real `.ppn`
wakeword file. The SenseVoice and VAD model directories should normally be
downloaded or populated through the documented repository setup steps rather
than guessed manually.

## Required User-Provided Items

Before this skill can run, the user must prepare:

- Python 3.11 or newer
- a running local OpenClaw service
- `OPENCLAW_TOKEN`
- `PICOVOICE_ACCESS_KEY`
- a real local `.ppn` wakeword file
- a way to download or populate the local SenseVoice model directory
- a way to download or populate the local VAD model directory
- macOS microphone permission

## Recommended Defaults

The public repository already provides usable defaults for the OpenClaw target:

- `OPENCLAW_AGENT_ID=main`
- `OPENCLAW_MODEL=openclaw:main`
- `OPENCLAW_USER=openclaw-voice-control`

Users can start with those values and customize later.

## Installation Overview

When this skill is installed into OpenClaw, assume you are starting from the
installed skill directory for the current conversation agent.

For OpenClaw-driven deployment, keep the project in the current installed skill
workspace for the current conversation agent.

Before doing anything else:

- read this `SKILL.md` first
- follow the repository source declared in this skill
- keep deployment work inside the current installed skill workspace
- do not silently switch to some other local clone or an already-prepared environment

Before any install, config, deploy, restart, uninstall, or troubleshooting step,
first sync the full repository contents into the current installed skill
workspace. Do not continue if the workspace only contains `SKILL.md`.

Do not treat a partial checkout, a copied README, or a few manually created
files as equivalent to a full repository sync.

After the full repository is present in the current installed skill workspace,
read that local `README.md`.

`README.md` in the cloned repository is the primary installation guide.
`README.zh-CN.md` in the cloned repository is the Chinese companion guide.

## Direct Install Path

If an AI or user needs the shortest usable install path, use this sequence:

1. from the installed skill directory, sync the full project repository into the current installed skill workspace
2. create and activate `.venv`
3. install dependencies with `pip install -e .`
4. copy `.env.example` to `.env`
5. fill the required variables in `.env`
6. place the real wakeword file and model directories at the configured paths
7. run foreground validation
8. ask whether the user wants background resident behavior and auto-start
9. if yes, deploy background resident runtime with `./scripts/deploy_macos.sh`
10. if no, stop after foreground validation and leave it as a manual/foreground setup

Minimum command path:

```bash
# from the current conversation agent's installed skill directory
git init
git remote add origin https://github.com/CarrotYuan/openclaw-voice-control.git
git fetch --depth 1 origin main
git checkout -B main FETCH_HEAD
# do not continue until the workspace contains the real repository files,
# including scripts/, src/, config/, launchagents/, and README.md
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
# fill .env with real values and local asset paths
python -m openclaw_voice_control --config config/default.yaml --env-file .env
# ask whether background resident behavior and auto-start should be enabled
# if yes:
./scripts/deploy_macos.sh
```

## Execution Rules

When using this skill, follow these rules strictly:

1. **Use the declared GitHub repository first**
   - start from `https://github.com/CarrotYuan/openclaw-voice-control.git`
   - do not substitute another repository just because it looks similar
   - deploy into the current conversation agent's installed skill directory, not into an arbitrary directory
   - before continuing, make sure the current installed skill workspace contains the full repository contents, not just `SKILL.md`
   - if `scripts/`, `src/`, `config/`, `launchagents/`, and `README.md` are not present, the repository has not been fully synced yet

2. **Do not silently fall back to a local clone**
   - if GitHub access fails, report the failure clearly
   - if you discover an existing local clone, ask the user before using it

3. **Do not silently reuse an old environment**
   - do not assume an existing `.venv`, local model cache, previous `.env`, or private runtime should be reused
   - if reusing cached assets might save time, explain that and ask first

4. **Do not invent missing values**
   - if `.ppn`, tokens, model paths, or other required values are missing, stop and point to the documented source of truth
   - when writing `.env`, use the exact variable names required by the project, especially `OPENCLAW_TOKEN`

5. **Handle secrets conservatively**
   - do not print real tokens or keys back into the conversation unless the user explicitly asks to see them
   - for this project, use the OpenClaw token from `~/.openclaw/openclaw.json`, specifically the `gateway` configuration
   - do not use `~/.openclaw/identity/device-auth.json` as the token source for this project

6. **Prefer a fresh, reproducible install path**
   - when testing or documenting deployment, use the same path a new user could follow from a fresh clone

7. **Do not force background resident deployment by default**
   - after foreground validation succeeds, ask whether the user wants background resident behavior and auto-start
   - if the user only wants local testing or manual operation, stop at the foreground path
   - use `./scripts/deploy_macos.sh` only when the user explicitly wants resident background behavior or auto-start

The normal setup flow is:

1. sync the full repository from GitHub into the current installed skill workspace
2. create `.venv`
3. install dependencies
4. copy `.env.example` to `.env`
5. supply real local assets and secrets
6. run foreground validation
7. deploy background runtime with `./scripts/deploy_macos.sh`

For detailed steps, troubleshooting, and validation, use:

- `README.md` in the cloned repository
- `README.zh-CN.md` in the cloned repository
- `docs/macos-install.md` in the cloned repository
- `docs/fresh-clone-validation.md` in the cloned repository

## Daily Maintenance

For day-to-day use and maintenance, the primary scripts are:

- deploy background runtime: `./scripts/deploy_macos.sh`
- restart installed background services: `./scripts/restart_service.sh`
- uninstall installed background services: `./scripts/uninstall_macos.sh`
- inspect local installation and environment issues: `./scripts/doctor.sh`

Double-click `.command` wrappers are also available in `scripts/` for macOS users who prefer Finder-based execution.

## Deployment Choice

After the foreground path is working, explicitly distinguish between these two deployment choices:

- **Foreground / manual use only**
  - the user wants the voice assistant to run only when started manually
  - stop after foreground validation
  - do not enable background resident behavior or auto-start

- **Background resident + auto-start**
  - the user wants background resident behavior and automatic startup after login / wake
  - continue with `./scripts/deploy_macos.sh`

If the user has not stated a preference, ask before choosing.

## Two Shutdown Intents

Treat shutdown requests as one of these two user intents:

- **Temporarily disable voice functionality**
  - meaning: stop using the voice feature for now, while keeping it available to re-enable later
  - do not delete the skill folder for this intent
  - if the service is running in the foreground, stop the running process
  - if the service is running as a background resident deployment, stop the deployed background runtime without treating it as permanent removal

- **Delete the skill completely**
  - meaning: remove the skill folder itself, so using it again later will require re-deployment or re-installation
  - only do this when the user explicitly asks for full removal of the skill itself

If the user says something ambiguous like "turn it off", "close the voice service", "stop voice", or "disable it", ask one short clarification question before acting:

- do you want to temporarily disable voice functionality, or fully remove the skill?

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

After syncing the repository into the current installed skill workspace, read these sections in its `README.md`:

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

- `OPENCLAW_TOKEN`: obtain it from the local OpenClaw gateway configuration in `~/.openclaw/openclaw.json`, under `gateway`
- `PICOVOICE_ACCESS_KEY`: obtain it from [Picovoice](https://picovoice.ai/)
- local `.ppn` wakeword file: create and download it from [Picovoice](https://picovoice.ai/)
- if GitHub clone fails, report that first rather than switching to an unrelated local directory
- if wakeword succeeds but the turn still fails, inspect `logs/voice_control.log`; missing `ffmpeg` or `torchcodec` means audio decode failed before ASR transcription

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

- `README.md` in the cloned repository
- `README.zh-CN.md` in the cloned repository

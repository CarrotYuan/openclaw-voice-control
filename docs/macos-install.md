# macOS Install

This first public rewrite is intentionally limited to macOS.

## Prerequisites

- macOS
- OpenClaw running locally and reachable
- microphone permission granted
- a wakeword route
  - default: openWakeWord with the built-in English `hey jarvis` model
  - optional: Picovoice Porcupine with your own `AccessKey` and `.ppn`

## Quick Start

1. Create a virtual environment.
2. Install the package in editable mode.
3. Copy `.env.example` to `.env`.
4. Fill in the required values.
5. Verify `config/default.yaml`.
6. Run the service from the repository root.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
python3 -m openclaw_voice_control --config config/default.yaml --env-file .env
```

If editable install fails on your machine because of PyPI SSL verification, retry with:

```bash
./.venv/bin/pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e .
```

## ASR Model Recommendation

For a more stable setup, prefer local model paths over first-run online model resolution.

For a clean new-environment setup, prepare explicit local model directories:

- `models/SenseVoiceSmall`
- `models/fsmn-vad`

Then point the config or `.env` at those directories.

For the default wakeword route, use:

- `WAKEWORD_PROVIDER=openwakeword`
- `OPENWAKEWORD_MODEL_NAME=hey jarvis`

That default route does not require a Picovoice key or a local `.ppn`.
The remaining local model files can normally be downloaded by the operator or
another AI during setup.

If you prefer the optional Porcupine route, use:

- `WAKEWORD_PROVIDER=porcupine`
- `WAKEWORD_FILE=assets/wakeword/your-model.ppn`
- or `WAKEWORD_FILE=/absolute/path/to/your-model.ppn`

The repository does not include a real `.ppn` file. You must provide your own local
wakeword asset if you choose Porcupine.

To switch to another official openWakeWord pretrained wakeword, change
`OPENWAKEWORD_MODEL_NAME`. Common examples include `hey jarvis`,
`hey mycroft`, `hey rhasspy`, and `alexa`. The selected pretrained model will
be downloaded automatically on first use.

For VAD, remember that the config alias `fsmn-vad` is a FunASR alias, not a direct
ModelScope repository id. Fresh-clone validation found that a direct command such
as `modelscope download --model fsmn-vad` is not enough.

If you need to populate `models/fsmn-vad`, use FunASR resolution first:

```bash
./.venv/bin/python - <<'PY'
from funasr import AutoModel
AutoModel(model='fsmn-vad', disable_update=True)
PY
```

Then copy the resolved model into `models/fsmn-vad`.

## Audio Device Diagnostics

If the service starts but never reacts to speech, inspect the visible input devices:

```bash
./.venv/bin/python scripts/list_audio_devices.py
```

Then test microphone capture directly:

```bash
./.venv/bin/python scripts/test_microphone.py --device -1 --seconds 3
```

If needed, set `audio.input_device_index` in `config/default.yaml`.

## SenseVoice Model Completeness Note

If wakeword detection works and the service enters listening, but recognized
text becomes obvious garbage, multilingual fragments, or random token-like
output, verify that the local SenseVoice model directory is complete.

In particular, check that the configured SenseVoice directory still contains:

- `model.pt`

A directory can exist while still being incomplete. If `model.pt` is missing,
ASR may appear to start but produce unusable output.

If needed, repopulate the full model directory:

```bash
./.venv/bin/modelscope download --model iic/SenseVoiceSmall --local_dir models/SenseVoiceSmall
```

## Why A New Environment Can Still Fail Even When Startup Looks Healthy

During validation, the repository could sometimes reach the idle listening stage
while a restricted execution context still failed live wakeword testing.

The reason is environmental:

- `sounddevice` may not see real Core Audio input devices
- `pvrecorder` may expose only `NULL Capture Device`
- direct microphone self-tests may fail before actual capture

This means "service starts" and "service can really hear speech" are separate
checks. The correct validation target is a normal macOS terminal or LaunchAgent
session running from this repository itself.

## Recommended Real-Machine Validation

After the direct dependency install is complete, validate from your own macOS terminal:

1. Stop any other voice service or overlay that may still be using the microphone.
1. Open Terminal on macOS as your normal user.
2. `cd` into the repository root.
3. Activate the repository `.venv`.
4. Run `./scripts/doctor.sh`.
5. Run `python -m openclaw_voice_control --config config/default.yaml --env-file .env`.
6. In a second terminal, run `python -m openclaw_voice_control.overlay_app --config config/default.yaml --env-file .env` if you want overlay coverage too.
7. Test wakeword, recording, ASR, OpenClaw reply, and TTS from that same repository-local session.

## Background Audio Permission Note

The most important macOS background risk discovered during fresh-clone validation
was the startup chain itself:

- `launchd -> shell -> bare python`

That path can be unreliable for microphone permission behavior on some macOS
systems.

The public repository now uses a project-owned host app launcher so the background
path becomes:

- `launchd -> host app -> shell script -> python`

`deploy_macos.sh` now builds the host apps automatically before bootstrapping the
LaunchAgents. This is the recommended background path.

The generated apps live under:

- `runtime/host_apps/OpenClawVoiceControlServiceHost.app`
- `runtime/host_apps/OpenClawVoiceControlOverlayHost.app`

The interpreter override variables still exist, but only as optional
machine-specific troubleshooting knobs:

- `VOICE_CONTROL_PYTHON_BIN`
- `VOICE_CONTROL_OVERLAY_PYTHON_BIN`

Do not assume background startup failed if it does not react immediately after
deploy. A cold start can still be loading ASR and initializing the wakeword
engine. The practical ready checkpoint is when logs reach:

- `Wakeword engine ready`
- `Entered idle listening loop`

## launchd Install

After the direct run works, install the LaunchAgent:

```bash
chmod +x scripts/*.sh
./scripts/deploy_macos.sh
```

This command also builds the host launcher apps before install.

## One-Click Remove

```bash
./scripts/uninstall_macos.sh
```

The uninstall script is expected to remove more than LaunchAgent plist files. It
also cleans up:

- LaunchAgent registrations
- generated host apps under `runtime/host_apps`
- matching host-app processes
- matching foreground Python test processes

## Preflight Check

Before direct run or deploy:

```bash
./scripts/doctor.sh
```

## Current Limits

- macOS only
- Chinese ASR by default
- overlay UI is migrated in a smaller public-first version, not a full visual clone yet
- wakeword asset redistribution is not handled by this repository yet

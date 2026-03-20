# macOS Install

This first public rewrite is intentionally limited to macOS.

## Prerequisites

- macOS
- OpenClaw running locally and reachable
- microphone permission granted
- a valid Picovoice access key
- a wakeword model you are allowed to use locally

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

## ASR Model Recommendation

For a more stable setup, prefer local model paths over first-run online model resolution.

If you already have local ModelScope cache directories, point the config to them:

- `asr.model_path`
- `asr.vad_model_path`

This reduces the chance of first-run failures caused by online model registration or download issues.

For wakeword, prefer an explicit absolute `.ppn` file path:

- `WAKEWORD_FILE=/absolute/path/to/your.ppn`

If `WAKEWORD_FILE` is not set, the config file should still point to a valid `.ppn` path instead of an empty placeholder.

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

## Why A Private Local Build Can Work While Another Test Context Fails

During validation, the public repository was able to reach the idle listening stage, but some restricted execution contexts still failed live wakeword testing.

The reason is environmental, not architectural:

- `sounddevice` could not see any real Core Audio input devices
- `pvrecorder` only exposed `NULL Capture Device`
- direct microphone self-tests failed before actual capture

This means a restricted or non-interactive process can be unable to access real microphone hardware even when the same code works from your normal macOS session.

If your private local project already works, that usually means it is benefiting from:

- a real GUI user session
- microphone permission already granted
- working Core Audio device visibility
- existing local model caches and wakeword assets

So the correct validation target for this public repository is a normal local macOS terminal or LaunchAgent session, not a restricted automation context alone.

## Recommended Real-Machine Validation

After the direct dependency install is complete, validate from your own macOS terminal:

1. Stop the old private voice service and overlay.
2. Open Terminal on macOS as your normal user.
3. `cd` into the public repository root.
4. Activate the repository `.venv`.
5. Run `./scripts/doctor.sh`.
6. Run `python -m openclaw_voice_control --config config/default.yaml --env-file .env`.
7. In a second terminal, run `python -m openclaw_voice_control.overlay_app --config config/default.yaml --env-file .env` if you want overlay coverage too.
8. Test wakeword, recording, ASR, OpenClaw reply, and TTS from that real local session.

## Background Audio Permission Note

If foreground terminal runs work but the LaunchAgent version still does not light up the microphone or react to wakeword, the most likely cause on macOS is the Python executable identity used by the background process.

In some macOS setups, an older trusted Python interpreter can behave differently from the repository-local interpreter when launched in the background.

The rewritten public repository normally uses its own interpreter inside `.venv/bin/python`.

Those can behave differently under macOS privacy controls when launched in the background.

To support this case, the public scripts now allow an explicit override:

- `VOICE_CONTROL_PYTHON_BIN`
- `VOICE_CONTROL_OVERLAY_PYTHON_BIN`

If you need to test whether background microphone access is tied to an already trusted interpreter, set in `.env`:

```bash
VOICE_CONTROL_PYTHON_BIN=/absolute/path/to/python
VOICE_CONTROL_OVERLAY_PYTHON_BIN=/absolute/path/to/python
```

Then redeploy the LaunchAgents and test again.

If you also want the public overlay:

```bash
python3 -m openclaw_voice_control.overlay_app --config config/default.yaml --env-file .env
```

## launchd Install

After the direct run works, install the LaunchAgent:

```bash
chmod +x scripts/*.sh
./scripts/deploy_macos.sh
```

## One-Click Remove

```bash
./scripts/uninstall_macos.sh
```

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

# Fresh Clone Validation

This document records the practical issues discovered while validating the public
repository from a fresh local clone on macOS.

It is intended to answer four questions clearly:

1. what was tested
2. what failed during the first clean setup
3. what the real root cause was
4. what fix is now implemented in this repository

## Validation Goal

The goal of this validation was not only to prove that the repository can start in
the foreground, but also to prove that a fresh clone can be taken from:

- clone
- virtual environment creation
- dependency install
- local asset preparation
- foreground smoke test
- background deployment
- background wakeword and auto-start behavior

That distinction matters because a repository can appear healthy while still failing
at the last macOS-specific background step.

## What Was Confirmed

During fresh-clone validation, the following were confirmed:

- clone into an empty directory succeeded
- `.venv` creation succeeded
- editable install succeeded
- `.env` could be created from `.env.example`
- core imports succeeded:
  - `openclaw_voice_control`
  - `torch`
  - `torchaudio`
  - `PySide6`
- the foreground service could reach:
  - `Loading ASR model...`
  - `ASR model ready`
  - `Wakeword engine ready`
  - `Entered idle listening loop`
- the overlay runtime could read and write the repository-local state files
- the rewritten background deployment path could be installed and launched through
  LaunchAgent
- product-level validation on the test machine later confirmed:
  - wakeword
  - reply playback
  - background resident behavior
  - auto-start

## What A Fresh Clone Does Not Include

These items are intentionally not bundled with the public repository:

- `.env`
- `OPENCLAW_TOKEN`
- `PICOVOICE_ACCESS_KEY`
- a real `.ppn` wakeword file
- SenseVoice model files
- VAD model files
- any private OpenClaw runtime

This means a fresh clone is expected to fail until the user supplies real local
assets and secrets.

## Problems Found During Fresh Clone Validation

### 1. Missing `.env`

Observed behavior:

- `doctor.sh` warned about missing `.env`
- background deploy scripts correctly refused to continue without local config

Root cause:

- the public repository intentionally does not include a real `.env`

Resolution:

- documented `cp .env.example .env`
- documented which fields still require real user input

Status:

- expected and documented

### 2. Missing wakeword and model assets after clone

Observed behavior:

- these paths did not exist right after clone:
  - `assets/wakeword/...`
  - `models/SenseVoiceSmall`
  - `models/fsmn-vad`

Root cause:

- the repository does not ship proprietary or machine-local runtime assets

Resolution:

- documented required user-provided assets in the main README and install docs
- clarified the recommended repository-local layout:
  - `assets/wakeword/your-model.ppn`
  - `models/SenseVoiceSmall`
  - `models/fsmn-vad`

Status:

- fixed in docs and sample config

### 3. Wakeword placeholder looked too much like a real bundled asset

Observed behavior:

- a concrete filename such as `hey-jarvis_en_mac_v4_0_0.ppn` can make users think
  the repository already includes a real wakeword asset

Root cause:

- the sample path looked like a shipped runtime file instead of a placeholder

Resolution:

- changed the public placeholder to:
  - `assets/wakeword/your-model.ppn`
- added stronger README wording that the repository does not ship a real `.ppn`

Status:

- fixed

### 4. `pip install -e .` could fail because of PyPI SSL verification

Observed behavior:

- editable install could fail while fetching build dependencies such as
  `setuptools>=68`
- the concrete failure was SSL certificate verification against `pypi.org`

Root cause:

- machine-specific or environment-specific TLS certificate trust issues

Working fallback:

```bash
./.venv/bin/pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e .
```

Resolution:

- recorded the fallback in repository documentation

Status:

- documented

### 5. `fsmn-vad` could not be downloaded directly through `modelscope download`

Observed behavior:

- `modelscope download --model fsmn-vad --local_dir models/fsmn-vad`
  failed because the short alias is not a valid ModelScope repository id

Root cause:

- `fsmn-vad` is a FunASR-friendly alias, not a direct ModelScope namespace/name

Resolved practical understanding:

- FunASR resolves `fsmn-vad` to:
  - `iic/speech_fsmn_vad_zh-cn-16k-common-pytorch`

Working preparation method:

```bash
./.venv/bin/python - <<'PY'
from funasr import AutoModel
AutoModel(model='fsmn-vad', disable_update=True)
PY
```

Then copy the resolved cache into:

- `models/fsmn-vad`

Status:

- documented

### 6. Foreground startup success did not guarantee real end-to-end success

Observed behavior:

- the service could start and load ASR
- that alone did not prove wakeword, microphone, OpenClaw request, and TTS all
  worked

Root cause:

- startup-only verification is weaker than interaction verification

Resolution:

- separated:
  - startup checks
  - microphone visibility checks
  - wakeword checks
  - background deployment checks

Status:

- documented

### 7. The biggest structural risk: background microphone permissions on macOS

Observed behavior:

- the older background path:
  - `launchd -> shell -> bare python`
  was not stable enough for microphone permission behavior on macOS

This was the most important problem found during the validation work.

Root cause:

- on macOS, the process chain used for background startup can materially affect how
  microphone permission and device visibility behave
- direct bare-Python LaunchAgent startup was not reliable enough as the primary
  design

Implemented fix:

- the repository now uses a project-owned host app launcher:
  - `launchd -> host app -> shell script -> python`

Implemented files:

- `scripts/openclaw_host_launcher.m`
- `scripts/build_host_apps.sh`
- `scripts/deploy_macos.sh`
- `launchagents/ai.openclaw.voice-control.plist`
- `launchagents/ai.openclaw.overlay.plist`

Validated outcome on the machine under test:

- real background startup succeeded
- wakeword succeeded
- reply succeeded
- background resident behavior succeeded
- auto-start succeeded

Status:

- fixed in architecture and validated locally

### 8. Background startup could be misread as failure when checked too early

Observed behavior:

- after deploy, the service could stay in:
  - `Loading ASR model...`
  - `Initializing wakeword engine...`
- this could make a real background startup look like a failed resident start if
  checked too early

Root cause:

- cold startup still needs time to load ASR and initialize the wakeword engine

Resolution:

- wait for logs to reach:
  - `Wakeword engine ready`
  - `Entered idle listening loop`
- treat those log lines as the real background-ready checkpoint

Status:

- documented

### 9. Uninstall originally left behind manual test processes

Observed behavior:

- foreground Python test runs could survive after uninstall
- generated host-app executables could also remain in `runtime/host_apps`
- this made it look like uninstall had failed even when LaunchAgents were gone

Root cause:

- removing plist files alone is not enough when validation also includes manual
  foreground test runs

Resolution:

- `uninstall_macos.sh` now removes:
  - LaunchAgent registrations
  - generated host apps under `runtime/host_apps`
  - matching host-app processes
  - matching foreground Python test processes

Status:

- fixed and documented

## Current Recommended Validation Order

For a new machine or a new local clone, validate in this order:

1. clone the repository
2. create `.venv`
3. install dependencies
4. create `.env` from `.env.example`
5. place the real `.ppn` and model directories locally
6. run `./scripts/doctor.sh`
7. run audio self-tests:
   - `scripts/list_audio_devices.py`
   - `scripts/test_microphone.py`
8. run the service in the foreground
9. run the overlay in the foreground if needed
10. deploy with `./scripts/deploy_macos.sh`
11. verify background wakeword and auto-start on the real machine

## Final Conclusion

Fresh-clone validation showed that the public repository was already structurally
close, but it also exposed one critical macOS-specific weakness:

- background startup through bare Python was not a stable foundation

That issue is now addressed by the repository-owned host app launcher. The current
repository should therefore be understood as:

- a public macOS voice-control repository that still requires user-supplied local
  assets
- but no longer depends on the older bare-Python LaunchAgent chain as its main
  background design

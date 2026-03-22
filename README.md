# OpenClaw Voice Control

[中文说明](README.zh-CN.md)

`OpenClaw Voice Control` is a local macOS voice-control companion for OpenClaw.

Current scope:

- macOS only
- Chinese ASR by default
- wakeword + local microphone capture + local TTS
- optional overlay UI
- launchd-based background operation on macOS

## What This Repo Does

This repository lets you:

- say a wakeword
- record a local voice query
- transcribe Chinese speech with FunASR / SenseVoice
- forward the request to a local OpenClaw agent
- play the reply with macOS TTS
- optionally show an overlay window
- install both the service and overlay as LaunchAgents

By default, the public version now targets the OpenClaw `main` agent so a user can start with the default setup and customize later.

## End-To-End Deployment Guide

This section is the main operating guide for a new machine.

It is written to cover the full path from:

- fresh clone
- local asset preparation
- foreground validation
- background LaunchAgent deployment
- successful resident wakeword behavior on macOS

The goal is that a human operator or another AI can follow this section alone and
get the repository running without having to guess hidden setup steps.

## What You Must Prepare Yourself

Before this repository can work on a new machine, prepare all of the following:

- a macOS machine
- Python 3.11 or newer
- a local OpenClaw service that is already running and reachable
- an OpenClaw token
- a Picovoice AccessKey
- a real `.ppn` wakeword file
- microphone permission on macOS
- local ASR model files

The repository does not bundle:

- `.env`
- a real `.ppn`
- SenseVoice model files
- VAD model files
- a preconfigured OpenClaw runtime

That is intentional. A fresh clone is expected to stay incomplete until those
local assets and secrets are provided.

## Required Variables

At minimum, these values must be set in `.env`:

- `OPENCLAW_BASE_URL`
- `OPENCLAW_TOKEN`
- `PICOVOICE_ACCESS_KEY`
- `WAKEWORD_FILE`
- `SENSEVOICE_MODEL_PATH`
- `SENSEVOICE_VAD_MODEL_PATH`

These have usable public defaults unless you want to customize them:

- `OPENCLAW_AGENT_ID=main`
- `OPENCLAW_MODEL=openclaw:main`
- `OPENCLAW_USER=openclaw-voice-control`

Optional troubleshooting variables:

- `VOICE_CONTROL_PYTHON_BIN`
- `VOICE_CONTROL_OVERLAY_PYTHON_BIN`

Those interpreter override variables are optional troubleshooting knobs only. The
recommended background path is the project-owned host app launcher built by
`deploy_macos.sh`.

## Recommended Local Layout

The cleanest layout on a fresh clone is:

- wakeword file:
  `assets/wakeword/your-model.ppn`
- SenseVoice model directory:
  `models/SenseVoiceSmall`
- VAD model directory:
  `models/fsmn-vad`

The repository uses the placeholder path:

- `assets/wakeword/your-model.ppn`

This is only an example. The repository does not ship that file.

## Where To Get Each Requirement

- `OPENCLAW_BASE_URL`
  Use the URL exposed by your local OpenClaw runtime.
- `OPENCLAW_TOKEN`
  Use a valid token from your OpenClaw setup. For this project, prefer the
  `gateway` configuration in `~/.openclaw/openclaw.json` rather than reading it
  from device identity files.
- `PICOVOICE_ACCESS_KEY`
  Create a free account in the [Picovoice Console](https://picovoice.ai/) and
  copy your AccessKey.
- `WAKEWORD_FILE`
  Create or download your own Porcupine `.ppn` file from the
  [Picovoice Console](https://picovoice.ai/).
- `SENSEVOICE_MODEL_PATH`
  Point this at a local SenseVoiceSmall model directory.
- `SENSEVOICE_VAD_MODEL_PATH`
  Point this at a local VAD model directory.

## Agent Safety Reminder

This repository provides a local voice entrypoint. It does not bind wakeword
activation to one specific person.

That means:

- anyone near the microphone can potentially trigger the assistant
- any tool, permission, or account reachable through the connected OpenClaw
  agent should be treated as reachable through voice

Recommended practice:

- add explicit safety constraints to the prompt or core instructions of the
  agent connected to this voice layer
- require confirmation for high-risk actions such as deletion, payments,
  external publishing, credential changes, or machine-control operations
- avoid giving the voice-facing agent broad autonomous control over sensitive
  tools, accounts, or destructive actions
- use least privilege when deciding which tools and permissions the connected
  agent can access

Treat the voice entrypoint as a shared trigger surface and design the target
agent prompt and permissions accordingly.

## Full Setup Flow

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd openclaw-voice-control
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Primary path:

```bash
pip install -e .
```

Alternative requirements-file path:

```bash
pip install -r requirements.txt
```

Important fresh-clone note:

On some macOS environments, `pip install -e .` can fail because of PyPI SSL
certificate verification problems while fetching build dependencies.

If that happens, retry with:

```bash
./.venv/bin/pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e .
```

### 4. Create `.env`

```bash
cp .env.example .env
```

### 5. Fill in `.env`

At minimum, fill:

- `OPENCLAW_BASE_URL`
- `OPENCLAW_TOKEN`
- `PICOVOICE_ACCESS_KEY`
- `WAKEWORD_FILE`
- `SENSEVOICE_MODEL_PATH`
- `SENSEVOICE_VAD_MODEL_PATH`

Example repository-local asset layout:

```bash
OPENCLAW_BASE_URL=http://127.0.0.1:18789/v1/chat/completions
OPENCLAW_TOKEN=replace_me
PICOVOICE_ACCESS_KEY=replace_me
WAKEWORD_FILE=assets/wakeword/your-model.ppn
SENSEVOICE_MODEL_PATH=models/SenseVoiceSmall
SENSEVOICE_VAD_MODEL_PATH=models/fsmn-vad
```

### 6. Prepare the wakeword file

Put your real `.ppn` file at the path you referenced in `.env`.

Example:

```text
assets/wakeword/your-model.ppn
```

Important:

- the repository does not provide a real `.ppn`
- do not commit your own `.ppn` into git unless you have clear redistribution rights
- when training or testing the wakeword in the Picovoice web workflow, make
  sure the test page clearly shows that the wakeword was triggered successfully
- if the wakeword does not trigger successfully there, local wakeword response
  may also fail after deployment

### 7. Prepare the SenseVoice model

One working way is:

```bash
./.venv/bin/modelscope download --model iic/SenseVoiceSmall --local_dir models/SenseVoiceSmall
```

After that, `SENSEVOICE_MODEL_PATH=models/SenseVoiceSmall` should be valid.

### 8. Prepare the VAD model

The config uses the short alias:

```text
fsmn-vad
```

Important fresh-clone detail:

- `fsmn-vad` works as a FunASR alias
- `fsmn-vad` is not a valid direct `modelscope download --model ...` repository id

Do not assume this works:

```bash
modelscope download --model fsmn-vad --local_dir models/fsmn-vad
```

Instead, let FunASR resolve it first:

```bash
./.venv/bin/python - <<'PY'
from funasr import AutoModel
AutoModel(model='fsmn-vad', disable_update=True)
PY
```

Then copy the resolved model directory into:

```text
models/fsmn-vad
```

### 9. Run preflight checks

```bash
./scripts/doctor.sh
./.venv/bin/python scripts/list_audio_devices.py
./.venv/bin/python scripts/test_microphone.py --device -1 --seconds 3
```

What you want to see:

- `doctor.sh` passes
- `list_audio_devices.py` shows a real input device, not only `NULL Capture Device`
- `test_microphone.py` reports changing RMS values when you speak

### 10. Test the service in the foreground

```bash
python -m openclaw_voice_control --config config/default.yaml --env-file .env
```

Healthy startup usually reaches:

- `Loading ASR model...`
- `ASR model ready`
- `Initializing wakeword engine...`
- `Wakeword engine ready`
- `Entered idle listening loop`

This proves:

- package install is usable
- config loading is working
- local model paths and `.ppn` path are valid

### 11. Test the overlay in the foreground

In a second terminal:

```bash
python -m openclaw_voice_control.overlay_app --config config/default.yaml --env-file .env
```

The overlay may stay hidden in `idle` state. That is normal.

It is expected to appear during:

- wakeword detection
- listening
- thinking
- reply playback

### 12. Test the real voice path in the foreground

Say a wakeword and a short voice request.

A meaningful foreground success looks like:

- wakeword triggers
- recording begins
- ASR finishes
- OpenClaw returns a reply
- TTS speaks the reply

### 13. Deploy background LaunchAgents

Terminal:

```bash
./scripts/deploy_macos.sh
```

Finder double-click:

- [deploy_macos.command](scripts/deploy_macos.command)

Important architecture note:

The biggest structural risk found during fresh-clone validation was the old
background path:

- `launchd -> shell -> bare python`

That path was not stable enough for microphone permission behavior on macOS.

This repository now uses:

- `launchd -> host app -> shell script -> python`

`deploy_macos.sh` builds the host apps automatically under:

- `runtime/host_apps/OpenClawVoiceControlServiceHost.app`
- `runtime/host_apps/OpenClawVoiceControlOverlayHost.app`

and then bootstraps LaunchAgents through those host app executables.

This is now the recommended background path.

### 14. Validate background resident behavior

After deployment:

- confirm the service stays running in the background
- confirm the microphone is actually being used
- say the wakeword again
- verify wakeword, reply, and overlay behavior without relying on the foreground terminal process

Important timing note:

Do not assume background startup failed if wakeword does not react immediately
after deploy. Real-machine validation showed that a cold background start can
spend noticeable time in:

- `Loading ASR model...`
- `Initializing wakeword engine...`

Wait until logs reach:

- `Wakeword engine ready`
- `Entered idle listening loop`

before concluding that resident startup failed.

### 15. Validate auto-start

After background deploy works:

- log out and log back in, or otherwise restart the user session
- confirm the service and overlay auto-start again
- test wakeword one more time

### 16. Restart or uninstall if needed

Restart:

```bash
./scripts/restart_service.sh
```

Finder:

- [restart_service.command](scripts/restart_service.command)

Uninstall:

```bash
./scripts/uninstall_macos.sh
```

Finder:

- [uninstall_macos.command](scripts/uninstall_macos.command)

Important uninstall note:

`uninstall_macos.sh` now removes more than LaunchAgent plist files. It also
attempts to clean up:

- LaunchAgent registrations
- generated host-app executables under `runtime/host_apps`
- matching host-app processes
- matching foreground Python test processes

This matters because manual foreground tests can otherwise remain alive and make
it look like uninstall only removed the overlay while the voice service is still
running.

It also matters because repeated validation showed that a foreground test
process can survive in parallel with the LaunchAgent-managed background service
and confuse later deployment or uninstall checks.

## Important Configuration Locations

- [.env.example](.env.example)
  Example environment variables
- [config/default.yaml](config/default.yaml)
  Runtime defaults
- [src/openclaw_voice_control/config.py](src/openclaw_voice_control/config.py)
  Config merge logic
- [requirements.txt](requirements.txt)
  Direct pip installation list

In practice:

- change secrets and file paths in `.env`
- change audio, TTS, ASR, wakeword, and overlay defaults in `config/default.yaml`
- only edit `config.py` if you are changing configuration behavior itself

## TTS Configuration

This project currently uses macOS `say` for reply playback.

The main TTS settings live in:

- [default.yaml](config/default.yaml) under `tts:`
- [tts.py](src/openclaw_voice_control/tts.py) for the actual playback implementation

The most important fields are:

- `tts.voice`
  Controls which macOS voice is used for spoken replies. The current default is `Yue`.
- `tts.wake_ack`
  Controls the short spoken acknowledgement after wakeword detection, for example `我在`.
- `tts.followup_beep_enabled`
  Enables or disables the short follow-up beep after a reply.
- `tts.followup_beep_sound`
  Controls the sound file used for the follow-up beep.
- `tts.record_done_beep_enabled`
  Enables or disables the beep after recording finishes.
- `tts.record_done_sound`
  Controls the sound file used after recording finishes.
- `tts.no_speech_beep_enabled`
  Enables or disables the beep for "no speech detected".
- `tts.no_speech_sound`
  Controls the sound file used for the no-speech case.
- `tts.post_reply_delay`
  Adds a short delay after reply playback if needed for smoother interaction timing.

To switch the speaking voice, edit this value in [default.yaml](config/default.yaml):

```yaml
tts:
  engine: macos_say
  voice: Tingting
```

To see the voices available on your own Mac, run:

```bash
say -v '?'
```

You can then replace `tts.voice` with any voice name returned by that command. For example:

- `Yue`
- `Tingting`
- `Sinji`
- `Meijia`

If you want a fully silent wake acknowledgement, you can also change:

```yaml
tts:
  wake_ack: ""
```

If you want the assistant to keep spoken replies but disable the extra beeps, set the corresponding `*_enabled` fields to `false`.

## Wakeword Note

This project uses Picovoice Porcupine for wakeword detection.

Users typically need both:

- a Picovoice `AccessKey`
- a `.ppn` wakeword model file

The `.ppn` file used on your own machine can come from the free Picovoice Console workflow, but this repository should not assume redistribution rights for a custom wakeword file. The safest public setup is:

- do not commit your real `.ppn` file
- tell users to generate or download their own
- let them point `WAKEWORD_FILE` at their local file

The sample repository path is intentionally a placeholder:

- `assets/wakeword/your-model.ppn`

It is not a bundled wakeword asset.

## What Can Be Configured

Users can change these without touching the main service code:

- OpenClaw base URL
- OpenClaw agent id
- OpenClaw model
- OpenClaw user id
- Picovoice AccessKey
- wakeword `.ppn` file path
- ASR model name
- ASR language
- local SenseVoice model path
- local VAD model path
- macOS TTS voice
- audio input device index
- overlay enable/disable
- background Python interpreter overrides
- host-app-based background deployment via `deploy_macos.sh`

Most of those values live in:

- [.env.example](.env.example)
- [default.yaml](config/default.yaml)

## Troubleshooting

### `pip install -e .` fails with SSL certificate verification

Retry with:

```bash
./.venv/bin/pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e .
```

### The service starts but cannot find the wakeword file

Check that `WAKEWORD_FILE` in `.env` points to a real local `.ppn`.

The repository placeholder:

```text
assets/wakeword/your-model.ppn
```

is not a bundled asset.

### `fsmn-vad` download does not work directly

That is expected. `fsmn-vad` is a FunASR alias, not a direct ModelScope repo id.

Use the FunASR resolution flow described above, then copy the resolved model into:

```text
models/fsmn-vad
```

### Foreground works but background does not react to speech

Treat these as separate checks:

- foreground startup
- foreground wakeword and reply
- background deployment
- background microphone visibility

The main background fix implemented in this repository is the host-app launcher
path used by `deploy_macos.sh`. Do not assume the older bare-Python LaunchAgent
path is still the recommended model.

### The overlay does not appear immediately

That can be normal. The overlay may remain hidden while the state is `idle`.

It should appear during:

- wakeword detection
- active listening
- thinking
- reply playback

### A new-environment test still fails on a machine that already has other voice tools

That usually means one of these is still true:

- the public repo is still missing a real `.env`
- the public repo is still missing a real `.ppn`
- local ASR model paths are not actually valid
- another voice service is still running and competing for the microphone
- the current execution context cannot see real Core Audio input devices
- background deployment was not done through the current host-app path

## Problems Found During Real Fresh-Clone Validation

The following problems were not theoretical. They were encountered during actual
repository validation from a fresh local clone.

### Missing runtime assets after clone

Observed:

- no `.env`
- no real `.ppn`
- no `models/SenseVoiceSmall`
- no `models/fsmn-vad`

Resolution:

- document all user-provided assets explicitly
- keep `.env.example` as template only
- use repository-local placeholder paths that clearly look like placeholders

### `.ppn` sample path looked too real

Observed:

- a concrete-looking filename can make users think the repository already bundles a
  real wakeword asset

Resolution:

- use `assets/wakeword/your-model.ppn` as the public placeholder
- state clearly that the repository does not ship a real `.ppn`

### Editable install could fail with PyPI SSL verification

Observed:

- `pip install -e .` could fail while fetching build dependencies

Resolution:

- retry with:

```bash
./.venv/bin/pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e .
```

### `fsmn-vad` could not be downloaded directly by its short alias

Observed:

- `modelscope download --model fsmn-vad` is not a valid direct repository id flow

Resolution:

- use FunASR alias resolution first
- then copy the resolved model into `models/fsmn-vad`

### Foreground startup success was not enough

Observed:

- foreground startup could succeed while end-to-end interaction or background
  behavior was still not proven

Resolution:

- separate validation into:
  - foreground startup
  - foreground interaction
  - background deployment
  - background wakeword and auto-start

### The most important structural issue: background microphone permissions on macOS

Observed:

- the older path
  - `launchd -> shell -> bare python`
  was not stable enough as the main macOS background architecture

Resolution:

- replace it with:
  - `launchd -> host app -> shell script -> python`
- make `deploy_macos.sh` build host apps automatically
- make LaunchAgents target the host app executables

Validated result:

- wakeword works
- reply works
- background resident behavior works
- auto-start works

### Background startup can be misread as failure if checked too early

Observed:

- after deploy, the service can still be loading ASR or initializing the
  wakeword engine
- this can look like "background did not stay resident" even though startup is
  still in progress

Resolution:

- check logs and wait for:
  - `Wakeword engine ready`
  - `Entered idle listening loop`

### Uninstall used to leave behind manual test processes

Observed:

- foreground Python test runs could survive uninstall
- generated host-app binaries could also remain in place
- this made it look like uninstall had failed even when LaunchAgents were gone

Resolution:

- `uninstall_macos.sh` now removes:
  - LaunchAgent registrations
  - generated host apps under `runtime/host_apps`
  - matching host-app processes
  - matching foreground Python test processes

## Important Current Limits

- macOS only
- Chinese ASR by default
- wakeword asset redistribution is not handled by this repository
- users still need to provide their own local `.ppn`, OpenClaw credentials, and ASR model directories

## Related Docs

- [macos-install.md](docs/macos-install.md)
- [fresh-clone-validation.md](docs/fresh-clone-validation.md)
- [same-machine-test.md](docs/same-machine-test.md)
- [architecture.md](docs/architecture.md)
- [release-checklist.md](docs/release-checklist.md)

## Release Note

This repository now uses the [MIT License](LICENSE).

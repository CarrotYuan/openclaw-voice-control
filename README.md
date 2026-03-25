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
- direct-run validation
- background LaunchAgent deployment
- successful resident wakeword behavior on macOS

The goal is that a human operator or another AI can follow this section alone and
get the repository running without having to guess hidden setup steps.

## What Must Exist Before Setup

Before this repository can work on a new machine, make sure all of the following
exist locally or can be provided during setup:

- a macOS machine
- Python 3.11 or newer
- a local OpenClaw service that is already running and reachable
- an OpenClaw token
- microphone permission on macOS
- a way to download the local ASR model files described below

By default, the repository now uses openWakeWord with the built-in English
`hey jarvis` model. That default route does not require a Picovoice account,
an access key, or a local `.ppn` file.

If you prefer the older Porcupine route, prepare these extra items as well:

- a Picovoice AccessKey
- a real `.ppn` wakeword file

The repository does not bundle:

- `.env`
- a real `.ppn`
- SenseVoice model files
- VAD model files
- a preconfigured OpenClaw runtime

That is intentional. A fresh clone is expected to stay incomplete until those
local assets and secrets are provided or downloaded through the documented
setup steps.

For the current default route, the practical split is:

- items that must already exist locally or be granted by the user
  - a running local OpenClaw service
  - a valid local OpenClaw token source
  - macOS microphone permission
- items that another AI or operator can usually fetch or populate automatically
  - `.env` created from `.env.example`
  - SenseVoice model files
  - VAD model files
  - the selected openWakeWord pretrained wakeword model on first run

## Required Variables

At minimum, these values must be set in `.env`:

- `OPENCLAW_BASE_URL`
- `OPENCLAW_TOKEN`
- `SENSEVOICE_MODEL_PATH`
- `SENSEVOICE_VAD_MODEL_PATH`

These have usable public defaults unless you want to customize them:

- `WAKEWORD_PROVIDER=openwakeword`
- `OPENWAKEWORD_MODEL_NAME=hey jarvis`
- `OPENCLAW_AGENT_ID=main`
- `OPENCLAW_MODEL=openclaw:main`
- `OPENCLAW_USER=openclaw-voice-control`

Only the optional Porcupine route needs these additional variables:

- `PICOVOICE_ACCESS_KEY`
- `WAKEWORD_FILE`

Optional troubleshooting variables:

- `VOICE_CONTROL_PYTHON_BIN`
- `VOICE_CONTROL_OVERLAY_PYTHON_BIN`

Those interpreter override variables are optional troubleshooting knobs only. The
recommended background path is the project-owned host app launcher built by
`deploy_macos.sh`.

## Recommended Local Layout

The cleanest layout on a fresh clone is:

- SenseVoice model directory:
  `models/SenseVoiceSmall`
- VAD model directory:
  `models/fsmn-vad`

If you use the optional Porcupine route, the recommended wakeword file path is:

- `assets/wakeword/your-model.ppn`

That path is only a placeholder. The repository does not ship a real `.ppn`.

## Where To Get Each Requirement

- `OPENCLAW_BASE_URL`
  Use the full chat completions endpoint exposed by your local OpenClaw runtime.
  Do not use only the host and port root. For the default local setup, use
  `http://127.0.0.1:18789/v1/chat/completions`.
- `OPENCLAW_TOKEN`
  Use a valid token from your OpenClaw setup. For this project, prefer the
  `gateway` configuration in `~/.openclaw/openclaw.json` rather than reading it
  from device identity files.
- default wakeword route
  Use openWakeWord with the built-in `hey jarvis` model. No Picovoice key or
  `.ppn` file is required for the default route.
- optional Porcupine wakeword route
  Create a free account in the [Picovoice Console](https://picovoice.ai/), copy
  your `PICOVOICE_ACCESS_KEY`, and create or download your own `.ppn` file for
  `WAKEWORD_FILE`.
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

### 5. Download the local ASR model directories

SenseVoice:

```bash
./.venv/bin/modelscope download --model iic/SenseVoiceSmall --local_dir models/SenseVoiceSmall
```

VAD:

```bash
./.venv/bin/python - <<'PY'
from funasr import AutoModel
AutoModel(model='fsmn-vad', disable_update=True)
PY
```

If you want the repository-local layout, copy or link the resolved VAD model
into:

```text
models/fsmn-vad
```

### 6. Fill in `.env`

At minimum, fill:

- `OPENCLAW_BASE_URL`
- `OPENCLAW_TOKEN`
- `SENSEVOICE_MODEL_PATH`
- `SENSEVOICE_VAD_MODEL_PATH`

Example repository-local asset layout:

```bash
OPENCLAW_BASE_URL=http://127.0.0.1:18789/v1/chat/completions
OPENCLAW_TOKEN=replace_me
WAKEWORD_PROVIDER=openwakeword
OPENWAKEWORD_MODEL_NAME=hey jarvis
OPENWAKEWORD_MODEL_PATH=
PICOVOICE_ACCESS_KEY=
WAKEWORD_FILE=assets/wakeword/your-model.ppn
SENSEVOICE_MODEL_PATH=models/SenseVoiceSmall
SENSEVOICE_VAD_MODEL_PATH=models/fsmn-vad
```

### 7. Prepare the wakeword provider

#### Default route: openWakeWord `hey jarvis`

No extra wakeword asset is required for the default route.

Use:

```text
WAKEWORD_PROVIDER=openwakeword
OPENWAKEWORD_MODEL_NAME=hey jarvis
```

On first run, openWakeWord will download the official pretrained `hey jarvis`
model set automatically and use that bundled English wakeword.

The wakeword threshold is already set in the repository configuration. Only
change it when troubleshooting retriggering or missed wakeups.

To switch to another official openWakeWord pretrained wakeword, change:

```text
OPENWAKEWORD_MODEL_NAME=hey mycroft
```

Common official pretrained examples include:

- `hey jarvis`
- `hey mycroft`
- `hey rhasspy`
- `alexa`

The selected pretrained model is downloaded automatically on first use.

The code path already supports changing `OPENWAKEWORD_MODEL_NAME`, but only the
default `hey jarvis` route has been smoke-tested in this repository so far.

#### Optional route: Picovoice Porcupine

If you want to keep using a custom `.ppn`, switch to:

```text
WAKEWORD_PROVIDER=porcupine
PICOVOICE_ACCESS_KEY=...
WAKEWORD_FILE=assets/wakeword/your-model.ppn
```

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

### 10. Start the service directly for testing

Direct-run validation is a two-process test.

Do not start only the voice service or only the overlay.

From the repository root in the first terminal:

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
- local model paths and wakeword provider configuration are valid

### 11. Start the overlay directly for testing

From the same repository root in a second terminal:

```bash
python -m openclaw_voice_control.overlay_app --config config/default.yaml --env-file .env
```

The overlay may stay hidden in `idle` state. That is normal.

It is expected to appear during:

- wakeword detection
- listening
- thinking
- reply playback

### 12. Test the real voice path with direct-run validation

For a complete direct-run test, both commands above must still be running at
the same time.

Say a wakeword and a short voice request.

A meaningful direct-run success looks like:

- wakeword triggers
- recording begins
- ASR finishes
- OpenClaw returns a reply
- TTS speaks the reply

Important next-step reminder:

Before doing anything after a direct-run test, stop that test first.

That includes actions such as:

- deploying background resident behavior
- validating auto-start
- starting another direct-run test

If the old direct-run service and overlay are left running, you can end up with
two active voice runtimes at the same time, which can trigger two wakeword
responses and two replies.

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
- verify wakeword, reply, and overlay behavior without relying on the direct-run terminal process

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
- matching direct-run Python test processes

This matters because direct-run tests can otherwise remain alive and make
it look like uninstall only removed the overlay while the voice service is still
running.

It also matters because repeated validation showed that a direct-run test
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

That means wakeword tuning values such as the openWakeWord threshold or the
post-turn rearm timing should normally be adjusted in `config/default.yaml`,
not added to `.env` unless you are debugging a specific machine.

## TTS Configuration

This project currently uses macOS `say` for reply playback.

The main TTS settings live in:

- [default.yaml](config/default.yaml) under `tts:`
- [tts.py](src/openclaw_voice_control/tts.py) for the actual playback implementation

The most important fields are:

- `tts.voice`
  Controls which macOS voice is used for spoken replies. The current default is `Tingting`.
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

If you change the speaking voice, first download that voice in macOS:

- System Settings
- Accessibility
- Spoken Content
- the `i` button next to System Voice
- Language
- Voice

If the target voice has not been downloaded there first, `say` may fail or fall
back to a different installed voice.

You can then replace `tts.voice` with any voice name returned by that command. For example:

- `Tingting`
- `Yue`
- `Sinji`
- `Meijia`

If you want a fully silent wake acknowledgement, you can also change:

```yaml
tts:
  wake_ack: ""
```

If you want the assistant to keep spoken replies but disable the extra beeps, set the corresponding `*_enabled` fields to `false`.

## Wakeword Note

This project now defaults to openWakeWord with the built-in English
`hey jarvis` model.

That default route does not require:

- a Picovoice `AccessKey`
- a local `.ppn` wakeword model file

If you prefer the optional Porcupine route, users typically need both:

- a Picovoice `AccessKey`
- a `.ppn` wakeword model file

The `.ppn` file used on your own machine can come from the free Picovoice
Console workflow, but this repository should not assume redistribution rights
for a custom wakeword file. The safest public setup is:

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
- wakeword provider
- openWakeWord model name
- openWakeWord model path
- openWakeWord threshold
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

This only applies when `WAKEWORD_PROVIDER=porcupine`.

Check that `WAKEWORD_FILE` in `.env` points to a real local `.ppn`.

The repository placeholder:

```text
assets/wakeword/your-model.ppn
```

is not a bundled asset.

### openWakeWord keeps retriggering even when nobody continues speaking

If the default `hey jarvis` route wakes successfully but then keeps retriggering
every few seconds when the room is otherwise quiet, the openWakeWord threshold
is too low for that microphone/environment combination.

Raise:

```text
OPENWAKEWORD_THRESHOLD=0.75
```

If needed, try values in the `0.65` to `0.85` range until false triggers stop
while normal wakeword use still works.

### `fsmn-vad` download does not work directly

That is expected. `fsmn-vad` is a FunASR alias, not a direct ModelScope repo id.

Use the FunASR resolution flow described above, then copy the resolved model into:

```text
models/fsmn-vad
```

### ASR starts but the recognized text is obvious garbage

If wakeword detection works, the service enters listening, and the recognized
text looks like multilingual garbage or random token fragments, check whether
the local SenseVoice model directory is actually complete.

In particular, verify that `models/SenseVoiceSmall` (or whatever
`SENSEVOICE_MODEL_PATH` points to) still contains the core model weight file:

- `model.pt`

A directory that exists but is missing `model.pt` or other core files can still
look "present" while producing broken ASR output.

If needed, re-download or re-copy the full model directory:

```bash
./.venv/bin/modelscope download --model iic/SenseVoiceSmall --local_dir models/SenseVoiceSmall
```

Do not treat "directory exists" as sufficient validation. The model contents
must be complete.

### Foreground works but background does not react to speech

Treat these as separate checks:

- direct-run startup
- direct-run wakeword and reply
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

- direct-run startup could succeed while end-to-end interaction or background
  behavior was still not proven

Resolution:

- separate validation into:
  - direct-run startup
  - direct-run interaction
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

- direct-run Python test runs could survive uninstall
- generated host-app binaries could also remain in place
- this made it look like uninstall had failed even when LaunchAgents were gone

Resolution:

- `uninstall_macos.sh` now removes:
  - LaunchAgent registrations
  - generated host apps under `runtime/host_apps`
  - matching host-app processes
  - matching direct-run Python test processes

## Important Current Limits

- macOS only
- Chinese ASR by default
- wakeword asset redistribution is not handled by this repository
- users still need to provide OpenClaw credentials and ASR model directories
- users only need their own local `.ppn` if they choose the optional Porcupine route

## Related Docs

- [macos-install.md](docs/macos-install.md)
- [fresh-clone-validation.md](docs/fresh-clone-validation.md)
- [same-machine-test.md](docs/same-machine-test.md)
- [architecture.md](docs/architecture.md)
- [release-checklist.md](docs/release-checklist.md)

## Release Note

This repository now uses the [MIT License](LICENSE).

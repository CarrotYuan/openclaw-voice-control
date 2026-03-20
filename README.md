# OpenClaw Voice Control

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

## What You Must Prepare Yourself

Before this repository can work on a new machine, the user must prepare all of the following:

- a macOS machine
- a local OpenClaw service that is already running and reachable
- an OpenClaw token
- a Picovoice AccessKey
- a `.ppn` wakeword file
- microphone permission on macOS
- Python 3.11 or newer and the ability to create a virtual environment
- local ASR model files, or a plan for how to obtain them

These values are expected through `.env` and config:

- `OPENCLAW_BASE_URL`
- `OPENCLAW_TOKEN`
- `OPENCLAW_AGENT_ID`
- `OPENCLAW_MODEL`
- `OPENCLAW_USER`
- `PICOVOICE_ACCESS_KEY`
- `WAKEWORD_FILE`
- `SENSEVOICE_MODEL_PATH`
- `SENSEVOICE_VAD_MODEL_PATH`

Optional machine-specific overrides:

- `VOICE_CONTROL_PYTHON_BIN`
- `VOICE_CONTROL_OVERLAY_PYTHON_BIN`

Those Python override variables are mainly for compatibility with your current machine. They should not be treated as a universal requirement for all users.

## How To Prepare Those Requirements

This section explains how a new user is expected to obtain the required pieces before deployment.

- `OPENCLAW_BASE_URL`
  Get this from your local OpenClaw runtime. This repository expects an already running local OpenClaw service.
- `OPENCLAW_TOKEN`
  Use a valid OpenClaw token from your own local setup.
- `OPENCLAW_AGENT_ID`, `OPENCLAW_MODEL`, `OPENCLAW_USER`
  The public default is now the OpenClaw `main` agent. If your local setup already works with the default agent, you may not need to change these.
- `PICOVOICE_ACCESS_KEY`
  Create a free account in the Picovoice Console and copy your AccessKey.
- `WAKEWORD_FILE`
  Create or download your own Porcupine `.ppn` wakeword file from Picovoice Console and point this variable to the local file path.
  The repository does not ship that `.ppn` file for you.
- `SENSEVOICE_MODEL_PATH`
  Point this to your local SenseVoice model directory if you already have the model cached or downloaded.
- `SENSEVOICE_VAD_MODEL_PATH`
  Point this to your local VAD model directory.
- microphone permission
  Grant microphone access to the terminal or background process on macOS when prompted.
- Python environment
  Create a virtual environment and install the package with `pip install -e .`

Recommended local placement on a new machine:

- wakeword file
  You can keep your `.ppn` anywhere on disk, but the simplest public-repo-friendly option is to place it under `assets/wakeword/` inside the repo and set `WAKEWORD_FILE=assets/wakeword/your-file.ppn`.
- SenseVoice model directory
  If you already have a local ModelScope cache, you can point `SENSEVOICE_MODEL_PATH` directly there. If you manage models manually, place the full SenseVoice model folder under `models/SenseVoiceSmall/` and point the variable at that directory.
- VAD model directory
  Use the same approach as SenseVoice. A stable relative path such as `models/fsmn-vad/` is fine as long as `SENSEVOICE_VAD_MODEL_PATH` points to the actual model directory.

## Important Configuration Locations

Users mainly need to adjust these files:

- [.env.example](.env.example)
  This shows the environment variables that should be copied into `.env`
- [default.yaml](config/default.yaml)
  This holds runtime defaults such as audio thresholds, ASR defaults, overlay settings, and fallback paths
- [config.py](src/openclaw_voice_control/config.py)
  This is where environment variables and config values are merged
- [requirements.txt](requirements.txt)
  This provides a direct pip-installable dependency list for users who prefer `pip install -r`

In practice:

- change connection and secret values in `.env`
- change audio, ASR, wakeword, overlay, and TTS defaults in `config/default.yaml`
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

## Full Setup Flow

This is the intended user flow from clone to deploy.

1. Clone the repository.

```bash
git clone <your-repo-url>
cd openclaw-voice-control
```

2. Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the package.

```bash
pip install -e .
```

If you prefer a direct requirements file install, use:

```bash
pip install -r requirements.txt
```

4. Create your local config file.

```bash
cp .env.example .env
```

5. Fill in at least these values in `.env`:

- `OPENCLAW_BASE_URL`
- `OPENCLAW_TOKEN`
- `PICOVOICE_ACCESS_KEY`
- `WAKEWORD_FILE`
- `SENSEVOICE_MODEL_PATH`
- `SENSEVOICE_VAD_MODEL_PATH`

The default OpenClaw values now assume the default `main` agent:

- `OPENCLAW_AGENT_ID=main`
- `OPENCLAW_MODEL=openclaw:main`
- `OPENCLAW_USER=openclaw-voice-control`

If a user has a custom OpenClaw agent, they can change those values later.

6. Run the built-in checks.

```bash
./scripts/doctor.sh
./.venv/bin/python scripts/list_audio_devices.py
./.venv/bin/python scripts/test_microphone.py --device -1 --seconds 3
```

7. Test the service in the foreground first.

```bash
python -m openclaw_voice_control --config config/default.yaml --env-file .env
```

8. If you want to test the overlay in the foreground too, open a second terminal:

```bash
python -m openclaw_voice_control.overlay_app --config config/default.yaml --env-file .env
```

9. After foreground testing works, deploy the background services.

Terminal:

```bash
./scripts/deploy_macos.sh
```

Finder double-click:

- [deploy_macos.command](scripts/deploy_macos.command)

If you later need to restart the background voice service:

Terminal:

```bash
./scripts/restart_service.sh
```

Finder double-click:

- [restart_service.command](scripts/restart_service.command)

10. If needed, remove the installed LaunchAgents.

Terminal:

```bash
./scripts/uninstall_macos.sh
```

Finder double-click:

- [uninstall_macos.command](scripts/uninstall_macos.command)

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

Most of those values live in:

- [.env.example](.env.example)
- [default.yaml](config/default.yaml)

## Important Current Limits

- macOS only
- Chinese ASR by default
- wakeword asset redistribution is not handled by this repository
- users still need to provide their own local `.ppn`, OpenClaw credentials, and ASR model directories
- choose and add a real `LICENSE` file before public GitHub release

## Related Docs

- [macos-install.md](docs/macos-install.md)
- [same-machine-test.md](docs/same-machine-test.md)
- [architecture.md](docs/architecture.md)
- [release-checklist.md](docs/release-checklist.md)

## Release Note

This repository now uses the [MIT License](LICENSE).

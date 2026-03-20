# Same-Machine Isolation Test

This document describes how to validate the public repository on the same Mac while
still treating the repository as a self-contained environment.

## Goal

Verify that the public repository can run from its own files, paths, scripts, and launch agents.

## Important Limit

This is a strong validation step, but not a perfect clean-room install.

Because the test still runs on the same machine, some things outside the
repository may already exist:

- microphone permissions
- OpenClaw itself
- downloaded model files
- local wakeword assets

There is one more practical limit that matters for voice testing:

- not every execution context on macOS can see real microphone devices

For example, the service can boot, load ASR, initialize the wakeword engine, and enter the idle listening loop from the public repository, while a restricted execution context still cannot see real Core Audio inputs.

That means "service starts" and "service can hear speech" are separate checks.

Fresh-clone validation added one more important lesson:

- background success on macOS must be tested through the real repository deployment
  path, not only through a foreground terminal run
- the current recommended background path is the host-app launcher built by
  `./scripts/deploy_macos.sh`

## Recommended Procedure

1. Stop any other voice service that may still be using the microphone.
2. Confirm any previous LaunchAgents are no longer active.
3. Open a normal macOS Terminal session as your logged-in user.
4. Work only inside the public repository directory.
5. Create a fresh `.env` from `.env.example`.
6. Run `./scripts/doctor.sh`.
7. Run `./scripts/list_audio_devices.py` or `./.venv/bin/python scripts/list_audio_devices.py` and confirm real input devices are visible.
8. Run the public service directly.
9. Run the public overlay directly if needed.
10. If direct runs work, test `./scripts/deploy_macos.sh`.
11. After validation, test `./scripts/uninstall_macos.sh`.

## What Counts As Success

- the service starts from the public repository
- the terminal session can see a real input device instead of only `NULL Capture Device`
- the overlay reads the public repository runtime state file
- no script depends on an unrelated local project directory
- launchd labels come from the public repository templates
- the service reacts to an actual wakeword spoken in that local session

## Manual Checks

Check the running command paths:

```bash
ps aux | grep openclaw_voice_control | grep -v grep
ps aux | grep openclaw_voice_control.overlay_app | grep -v grep
```

Check the launch agents:

```bash
launchctl print "gui/$(id -u)/ai.openclaw.voice-control" | sed -n '1,40p'
launchctl print "gui/$(id -u)/ai.openclaw.overlay" | sed -n '1,40p'
```

Check the runtime files:

```bash
ls -la runtime/
tail -f logs/voice_control.log
```

Check that audio devices are really visible:

```bash
./.venv/bin/python scripts/list_audio_devices.py
./.venv/bin/python scripts/test_microphone.py --device -1 --seconds 3
```

## If The Test Fails

The most common causes are:

- missing `.env`
- missing dependency installation
- wakeword asset path not available yet
- `.ppn` placeholder mistaken for a real bundled repository asset
- VAD model not actually prepared under `models/fsmn-vad`
- FunASR or Porcupine packages not installed
- editable install blocked by PyPI SSL verification issues
- another voice service is still running and masking the issue
- the current terminal or execution context cannot see microphone devices even though macOS itself has them
- the user is still testing the older bare-Python background path instead of the
  current host-app deployment path

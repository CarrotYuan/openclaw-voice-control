# Same-Machine Isolation Test

This document describes how to validate the public repository on the same Mac without relying on the old private runtime.

## Goal

Verify that the public repository can run from its own files, paths, scripts, and launch agents.

## Important Limit

This is a strong validation step, but not a perfect clean-room install.

Because the test still runs on the same machine, some things may already exist:

- microphone permissions
- OpenClaw itself
- cached model files
- local wakeword assets

There is one more practical limit that matters for voice testing:

- not every execution context on macOS can see real microphone devices

For example, the service can boot, load ASR, initialize the wakeword engine, and enter the idle listening loop from the public repository, while a restricted execution context still cannot see real Core Audio inputs.

That means "service starts" and "service can hear speech" are separate checks.

## Recommended Procedure

1. Stop the old private voice-control service.
2. Stop the old private overlay service.
3. Confirm the old LaunchAgents are no longer active.
4. Open a normal macOS Terminal session as your logged-in user.
5. Work only inside the public repository directory.
6. Create a fresh `.env` from `.env.example`.
7. Run `./scripts/doctor.sh`.
8. Run `./scripts/list_audio_devices.py` or `./.venv/bin/python scripts/list_audio_devices.py` and confirm real input devices are visible.
9. Run the public service directly.
10. Run the public overlay directly if needed.
11. If direct runs work, test `./scripts/deploy_macos.sh`.
12. After validation, test `./scripts/uninstall_macos.sh`.

## What Counts As Success

- the service starts from the public repository
- the terminal session can see a real input device instead of only `NULL Capture Device`
- the overlay reads the public repository runtime state file
- no script falls back to the old private directory
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
- FunASR or Porcupine packages not installed
- an old private service is still running and masking the issue
- the current terminal or execution context cannot see microphone devices even though macOS itself has them

# Release Checklist

## Safety

- remove all secrets and rotate any token that ever appeared in tracked files
- exclude logs, runtime files, local caches, and virtual environments
- confirm wakeword assets can be redistributed
- confirm any third-party code is linked, not copied blindly

## Engineering

- remove all absolute paths
- centralize config loading
- split service logic from UI and install scripts
- add dependency installation instructions
- add a minimal smoke test path
- keep fresh-clone validation notes updated when setup or deployment behavior changes
- keep background macOS deployment aligned with the host-app launcher architecture

## Fresh Clone Lessons To Preserve

Do not lose these documented lessons from clean-machine validation:

- the repository does not bundle `.env`, `.ppn`, SenseVoice, or VAD model assets
- `.ppn` placeholders must look like placeholders, not shipped assets
- `pip install -e .` may need a trusted-host fallback on some macOS machines
- `fsmn-vad` is a FunASR alias, not a direct ModelScope repo id
- foreground startup is weaker than full wakeword and background validation
- the biggest macOS risk was the old bare-Python LaunchAgent chain, which is now
  replaced by the host-app launcher path

## Publishing

- choose a public license
- write a public README with install and troubleshooting sections
- add plugin manifest after runtime boundaries are stable
- add `SKILL.md` only after plugin behavior is clear and documented

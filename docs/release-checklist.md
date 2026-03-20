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

## Publishing

- choose a public license
- write a public README with install and troubleshooting sections
- add plugin manifest after runtime boundaries are stable
- add `SKILL.md` only after plugin behavior is clear and documented

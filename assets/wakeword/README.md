# Wakeword Assets

The default public route now uses openWakeWord with the built-in English
`hey jarvis` model, so a fresh clone does not need any wakeword asset in this
directory.

This directory is only needed if you choose the optional Picovoice Porcupine
route and want to provide your own local `.ppn` file.

Recommended optional Porcupine usage:

- download or generate your own `.ppn` file from Picovoice Console
- place it here, for example `assets/wakeword/your-model.ppn`
- set `WAKEWORD_PROVIDER=porcupine` in `.env`
- set `WAKEWORD_FILE=assets/wakeword/your-model.ppn` in `.env`

Before adding binary model files, verify:

- license terms
- redistribution rights
- expected install path

# Wakeword Assets

This directory is the recommended place for your own local `.ppn` wakeword file.

The public repository does not include a real wakeword model. A fresh clone should
be treated as if this directory were empty.

Recommended usage:

- download or generate your own `.ppn` file from Picovoice Console
- place it here, for example `assets/wakeword/your-model.ppn`
- set `WAKEWORD_FILE=assets/wakeword/your-model.ppn` in `.env`

Before adding binary model files, verify:

- license terms
- redistribution rights
- expected install path

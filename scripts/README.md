# Scripts

This directory holds the public install and maintenance scripts.

- `deploy_macos.sh`
- `deploy_macos.command`
- `doctor.sh`
- `build_host_apps.sh`
- `start_service.sh`
- `start_overlay.sh`
- `restart_service.sh`
- `restart_service.command`
- `uninstall_macos.sh`
- `uninstall_macos.command`

These are public macOS scripts for service and overlay lifecycle management, including the host-app background startup path used for more reliable microphone permission behavior on macOS.

`uninstall_macos.sh` is also expected to clean up more than just plist files:

- LaunchAgent registrations
- generated host-app executables under `runtime/host_apps`
- matching host-app processes
- matching foreground Python test processes

This is important because manual foreground test runs can otherwise survive an
uninstall and make it look like background uninstall failed.

Use the `.sh` files from Terminal.
Use the `.command` files when you want a Finder-double-clickable entry point on macOS.

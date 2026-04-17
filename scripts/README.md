# Scripts

This folder holds helper scripts that were previously cluttering the repo root.

## Build

- `build/BUILD_APK.bat`: guided APK build flow
- `build/BUILD_APK_DEBUG.bat`: more verbose Windows build flow for troubleshooting
- `build/setup-build.bat`: prepares the Expo app for an APK build

## Deploy

- `deploy/DEPLOY_TO_PHONE.ps1`: interactive PowerShell helper for building and installing to a phone
- `deploy/DEPLOY.bat`: Windows deployment checklist
- `deploy/DEPLOY.sh`: Bash deployment checklist

These scripts now resolve the repo root from their own location, so they are safer to move around than before.

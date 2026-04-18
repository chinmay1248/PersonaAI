# PersonaAI Build And Install Guide

This guide is written for the current state of this repo on your machine.

## What Is Ready Right Now

- The backend API is implemented and tested.
- The Expo app bundles successfully for web.
- The app is already configured to use the production Railway backend:
  - `EXPO_PUBLIC_API_URL=https://personaai-backend-production-4490.up.railway.app/v1`
  - `EXPO_PUBLIC_ENV=production`
- WhatsApp capture and auto-training are implemented for Android native builds.

## Important Limitation

There is **no prebuilt APK file in this repo right now**.

That means:
- I can give you a downloadable **web build** right now.
- For an **Android APK**, you still need to run an EAS Android build or compile locally with a complete Android SDK setup.

## Download Links

Open these directly on your computer:

- Guide: [BUILD_AND_INSTALL_GUIDE.md](BUILD_AND_INSTALL_GUIDE.md)
- Web build zip: [PersonaAI-Web-Build.zip](../../artifacts/web/PersonaAI-Web-Build.zip)
- Web entry file: [index.html](../../personaai-app/dist/index.html)

## Option 1: Use The Downloadable Web Build Right Now

This is the fastest way to open PersonaAI immediately.

1. Open [PersonaAI-Web-Build.zip](../../artifacts/web/PersonaAI-Web-Build.zip)
2. Extract it anywhere
3. Open the extracted `index.html`

Or open the already generated file directly:

- [index.html](../../personaai-app/dist/index.html)

### What Works In The Web Build

- Login and registration
- Chat configuration
- Manual tone training
- Reply generation
- Conversation summarization

### What Does Not Work In The Web Build

- WhatsApp accessibility capture
- Android overlay button
- Automatic learning from WhatsApp messages

Those features require an Android native build.

## Option 2: Build An Android APK

Use this if you want PersonaAI on your phone with the WhatsApp integration path.

### Prerequisites

You need:

1. Node.js installed
2. Expo/EAS account
3. `eas-cli`

### Commands

Open Command Prompt or PowerShell and run:

```powershell
cd "c:\Users\DELL\Desktop\PersonaAI\personaai-app"
npm install
eas --version
```

If `eas` is missing:

```powershell
npm install -g eas-cli
```

Login once:

```powershell
eas login
```

Then build the APK:

```powershell
eas build --platform android --profile preview
```

### What Happens Next

- Expo uploads the project
- The APK is built in the cloud
- Expo gives you a download URL
- Download the `.apk` to your computer or phone

### Install On Phone

1. Download the APK from the Expo build URL
2. Transfer it to your Android phone if needed
3. Open it on the phone
4. Allow installation from unknown sources if Android asks
5. Install the app

## First Run Instructions

When the app opens:

1. Login screen appears
2. The login form is prefilled with:
   - Email: `demo@persona.ai`
   - Password: `StrongPass123`
3. Tap `Login`

Or create your own account from `Create an account`.

## Actual Onboarding Flow In This Project

After login:

1. Select your first chat
2. Choose the baseline personality
3. Paste a few sample messages to train tone
4. Finish the privacy/setup screen

After onboarding, go to:

- `Settings`

Then:

1. Add the WhatsApp groups you want to allow
2. Enable the WhatsApp extension toggle
3. Open Accessibility Settings
4. Open Overlay Permission
5. Turn on auto-training if you want live learning from outgoing messages

## How WhatsApp Integration Works

On Android native builds only:

- PersonaAI listens for WhatsApp screen content through Accessibility
- It matches only the groups you allowed
- It captures visible chat text
- It tries to separate incoming vs outgoing messages
- It can train your tone profile from outgoing messages
- It can feed captured chat text into reply generation and summarization

## Best Current Test Path

If you want to test the full product with the least friction:

1. Use the web build first to verify login, reply generation, and summarization
2. Use an Expo EAS Android build for phone testing
3. On Android, enable Accessibility and Overlay from Settings inside the app

## Troubleshooting

### Web build opens but API calls fail

Check internet access. The app is pointed at the production Railway backend.

### EAS build command fails

Run:

```powershell
cd "c:\Users\DELL\Desktop\PersonaAI\personaai-app"
npm install
npm install -g eas-cli
eas login
eas build --platform android --profile preview
```

### APK installs but WhatsApp capture does nothing

Check on the phone:

1. Accessibility permission is enabled
2. Overlay permission is enabled
3. The target WhatsApp group name is listed in `Settings`
4. Auto-training is enabled if you want background learning

## Current Status Summary

- Web build: ready now
- Android source: ready for build
- APK file in repo: not present
- Production backend: configured

## Recommended Download

Use this first:

- [PersonaAI-Web-Build.zip](../../artifacts/web/PersonaAI-Web-Build.zip)

Then build Android with:

```powershell
cd "c:\Users\DELL\Desktop\PersonaAI\personaai-app"
eas build --platform android --profile preview
```

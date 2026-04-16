# PersonaAI - Build and Install Guide (FOR YOUR PHONE)

## ✅ Configuration Complete!

Your `.env` file has been updated with:
```
EXPO_PUBLIC_API_URL=https://personaai-backend-production-4490.up.railway.app/v1
EXPO_PUBLIC_ENV=production
EXPO_PUBLIC_APP_NAME=PersonaAI
```

This points to your Railway backend in production! ✅

---

## 🚀 STEP-BY-STEP BUILD INSTRUCTIONS

### **STEP 1: Open Command Prompt**
1. Press `Windows Key + R`
2. Type: `cmd`
3. Press Enter
4. You'll see a black terminal window

---

### **STEP 2: Navigate to App Directory**
Copy and paste this command:
```cmd
cd "c:\Users\DELL\Desktop\PersonaAI\personaai-app"
```
Press Enter.

**Expected output:**
```
C:\Users\DELL\Desktop\PersonaAI\personaai-app>
```

---

### **STEP 3: Verify Node.js and npm**
Run these commands to check your setup:

```cmd
node --version
```
You should see: `v24.14.1` (or similar)

```cmd
npm --version
```
You should see: `10.x.x` (or similar)

If either command fails, install Node.js from https://nodejs.org/

---

### **STEP 4: Install or Verify EAS CLI**
Run this command:
```cmd
eas --version
```

**If you see a version number** → Skip to STEP 5

**If you get "not found" error** → Run this:
```cmd
npm install -g eas-cli
```
Wait for installation to complete (2-3 minutes)

---

### **STEP 5: Login to EAS (First Time Only)**
If this is your first time:
```cmd
eas login
```

This will:
1. Open your browser
2. Ask you to sign up or login
3. Create free EAS account
4. Return to terminal

If you already have an EAS account, you can skip this.

---

### **STEP 6: Install Dependencies**
Run this command:
```cmd
npm install
```

**What this does:**
- Downloads all app dependencies
- Takes 3-5 minutes
- You'll see lots of text (this is normal)

**When it's done**, you'll see:
```
added X packages in X seconds
```

---

### **STEP 7: Verify Configuration**
Make sure `.env` is configured:
```cmd
type .env
```

You should see:
```
EXPO_PUBLIC_API_URL=https://personaai-backend-production-4490.up.railway.app/v1
EXPO_PUBLIC_ENV=production
EXPO_PUBLIC_APP_NAME=PersonaAI
```

---

### **STEP 8: Build APK (THIS IS THE MAIN BUILD)**

Now run the build command:
```cmd
eas build --platform android --profile preview
```

**What happens next:**
1. EAS uploads your code
2. Builds APK in the cloud (takes 5-15 minutes)
3. Shows a download link when complete
4. **Keep this terminal window open!**

**You'll see output like:**
```
Building Android app
Waiting for build to complete...
[████████████████████░░░░░░░░░░] 75%
...
Build succeeded!
Download your build: https://eas-builds.expo.dev/...
```

---

## 📱 ONCE BUILD IS COMPLETE:

### **STEP 9: Download the APK**
1. The terminal will show a download link (blue, clickable)
2. Click the link OR copy-paste in browser
3. File downloads: `PersonaAI.apk` (150-200 MB)

**Save it somewhere easy to find!** (Desktop recommended)

---

### **STEP 10: Transfer APK to Phone**

**Option A: USB Cable (FASTEST)**
1. Connect phone to computer with USB cable
2. On phone: Tap "Allow file access"
3. Open Windows File Manager
4. Navigate to: `C:\Users\DELL\Desktop`
5. Find: `PersonaAI.apk`
6. Drag & drop to phone's Download folder
7. Done! ✓

**Option B: Email (EASY)**
1. Email the APK file to yourself
2. Open email on phone
3. Download attachment
4. Move to Downloads folder

**Option C: Google Drive (CONVENIENT)**
1. Drag APK to Google Drive
2. Access Google Drive on phone
3. Download file

---

### **STEP 11: Install on Phone**

On your **Android phone**:

1. **Enable Unknown Sources** (one-time)
   - Settings → Security
   - Find "Unknown Sources"
   - Toggle ON
   - (May vary by Android version)

2. **Install APK**
   - Open Files app
   - Navigate to Downloads
   - Tap `PersonaAI.apk`
   - Tap "Install"
   - Wait 1-2 minutes for installation

3. **Done!**
   - Installation complete
   - App appears on home screen

---

### **STEP 12: Launch and Login**

1. Tap PersonaAI app icon
2. App opens (first launch takes 3-5 seconds)
3. You see **Login Screen**

**Choose ONE:**

**Option A: Demo Account (Test First)**
- Tap "Demo Login" button
- Pre-filled: `demo@persona.ai` / `StrongPass123`
- Auto-logs in

**Option B: Create Your Own Account**
- Tap "Sign Up"
- Enter: Name, Email, Password
- Tap "Create Account"
- Then Login

---

### **STEP 13: Complete 4-Step Onboarding**

After login, you'll see 4 screens:

1. **Upload Chat** - Skip (optional)
2. **Select Tone** - Pick 2 personality traits
3. **Notifications** - Enable (recommended)
4. **Welcome** - Tap "Start Using PersonaAI"

**You're done! ✅**

---

## 🎉 NOW YOU CAN:

1. **Generate Replies**
   - Home tab → Paste message → Generate Reply
   - Get 3 personalized suggestions
   - Tap to copy to clipboard

2. **View Training History**
   - History tab → See all learned patterns
   - Check "Last Update" time

3. **Customize**
   - Settings tab → Adjust tone/mood
   - Enable auto-training (optional)

4. **Share**
   - Tell friends!
   - They can download same APK

---

## ❓ TROUBLESHOOTING

### "EAS build failed"
```cmd
npm cache clean --force
npm install
eas build --platform android --profile preview
```

### "Build stuck or taking too long"
- Wait 15+ minutes (cloud build can be slow)
- Check internet connection
- Try again if it times out

### "APK won't install on phone"
- Uninstall old version first
- Enable Unknown Sources in Security settings
- Re-download APK (may be corrupted)

### "App crashes after opening"
- Force stop: Settings → Apps → PersonaAI → Force Stop
- Clear cache: Settings → Apps → PersonaAI → Clear Cache
- Reinstall APK

### "Can't login with demo account"
- Check internet on phone
- Verify Railway backend is running
- Try again in 1 minute

---

## 📊 EXPECTED TIMING

| Task | Time |
|------|------|
| npm install | 3-5 min |
| EAS build | 5-15 min |
| Download APK | 1-5 min |
| Transfer to phone | 1 min |
| Install on phone | 1-2 min |
| First launch | 3-5 sec |
| Onboarding | 2-3 min |
| **TOTAL** | **20-35 min** |

---

## ✅ YOU'RE ALL SET!

Everything is configured and ready to build. Just follow the commands above step-by-step, and you'll have PersonaAI on your phone in 20-35 minutes!

**Questions?** Check the troubleshooting section above!

---

## 🎯 QUICK COMMAND SUMMARY

If you prefer just the commands:

```cmd
cd "c:\Users\DELL\Desktop\PersonaAI\personaai-app"
node --version
npm --version
eas --version
npm install -g eas-cli  # Only if needed
eas login               # Only first time
npm install
eas build --platform android --profile preview
```

Then:
1. Click download link from terminal
2. Download APK
3. USB transfer to phone
4. Tap APK to install
5. Launch app
6. Login: demo@persona.ai / StrongPass123
7. Enjoy!

---

**Status:** ✅ Ready to Build  
**Backend:** Railway Production  
**API URL:** https://personaai-backend-production-4490.up.railway.app/v1  
**Profile:** preview (for testing)

---

**LET'S GOOO! 🚀**

# PersonaAI - Complete Phone Setup Guide

## 🎯 Overview
This guide walks you through building and installing the PersonaAI app on your Android phone in **3 major steps**:
1. Build APK on your computer
2. Transfer APK to phone
3. Install and configure on phone

---

## 📋 Prerequisites
Before starting, ensure you have:
- **Android Phone** (5.0+) with USB debugging enabled
- **USB Cable** (for file transfer)
- **Computer** with:
  - Node.js v16+ (`node --version`)
  - npm v7+ (`npm --version`)
  - Internet connection
- **GitHub Account** (for EAS authentication)
- **Backend Server Running** (local or Railway)
  - Backend URL: `http://localhost:8000/v1` OR your Railway URL

---

## 🚀 STEP 1: Build APK on Computer

### Option A: Use Automated Script (RECOMMENDED)
Run the automated deployment script that handles everything:

```powershell
# Open PowerShell in PersonaAI directory
cd C:\Users\DELL\Desktop\PersonaAI
powershell -ExecutionPolicy Bypass -File .\scripts\deploy\DEPLOY_TO_PHONE.ps1
```

**What this script does:**
1. ✓ Checks Node.js, npm, EAS CLI
2. ✓ Installs EAS CLI if needed
3. ✓ Configures .env file (asks for API URL)
4. ✓ Installs npm dependencies
5. ✓ Builds APK (preview or production)
6. ✓ Shows download link

### Option B: Manual Build Steps

#### Step 1.1: Install EAS CLI
```bash
npm install -g eas-cli
```

#### Step 1.2: Login to EAS
```bash
eas login
# Opens browser → Sign in/Create account (free tier available)
# Confirm in terminal
```

#### Step 1.3: Configure .env File
Edit `personaai-app\.env`:

```env
# For LOCAL COMPUTER:
EXPO_PUBLIC_API_URL=http://localhost:8000/v1

# For LAN IP (if phone on same network):
EXPO_PUBLIC_API_URL=http://192.168.1.YOUR_COMPUTER_IP:8000/v1

# For RAILWAY/PRODUCTION:
EXPO_PUBLIC_API_URL=https://your-railway-domain.up.railway.app/v1

EXPO_PUBLIC_ENV=production
EXPO_PUBLIC_APP_NAME=PersonaAI
```

#### Step 1.4: Navigate to App Directory
```bash
cd C:\Users\DELL\Desktop\PersonaAI\personaai-app
```

#### Step 1.5: Install Dependencies
```bash
npm install
```

#### Step 1.6: Build APK
```bash
# For testing (faster, ~5-10 min):
eas build --platform android --profile preview

# For release (optimized, ~10-15 min):
eas build --platform android --profile production
```

**Output:**
- Wait for "Build successful" message
- Copy the download link from the output

---

## 📱 STEP 2: Download and Transfer APK to Phone

### Step 2.1: Download APK
1. Open the download link from build output
2. Click "Download" button
3. Save file: `PersonaAI.apk`

### Step 2.2: Transfer to Phone
Choose ONE method:

**Method A: USB Cable (RECOMMENDED)**
1. Connect Android phone to computer with USB cable
2. On phone: Allow USB file transfer
3. Open File Manager on computer → Phone storage
4. Create/navigate to `Download` folder
5. Drag & drop `PersonaAI.apk` to phone

**Method B: Email**
1. Attach `PersonaAI.apk` to email
2. Open email on phone
3. Download attachment

**Method C: Cloud Storage**
1. Upload `PersonaAI.apk` to Google Drive
2. Open Google Drive on phone
3. Download file to Downloads folder

**Method D: QR Code**
1. EAS build page has QR code → Scan with phone
2. Download directly

---

## 📲 STEP 3: Install on Phone

### Step 3.1: Enable Unknown Sources
1. Open **Settings** → **Security**
2. Enable **Unknown Sources** / **Install unknown apps**
   - May vary by Android version
3. Allow from Files app or browser

### Step 3.2: Install APK
1. Open **Files** / **File Manager** app
2. Navigate to **Downloads** folder
3. Tap on `PersonaAI.apk`
4. Tap **Install**
5. Wait for installation to complete
6. Tap **Open** (or find app in home screen)

### Step 3.3: First Launch
1. App opens with login screen
2. Click **"Sign Up"** or **"Demo Login"**

---

## ✅ STEP 4: First-Time Setup on Phone

### For Demo User (Recommended First Time)
1. Tap **"Demo Login"** button
2. Auto-fills: `demo@persona.ai` / `StrongPass123`
3. Tap **Login**

### For Your Own Account
1. Tap **Sign Up**
2. Enter:
   - Name
   - Email (e.g., yourname@example.com)
   - Password (min 8 chars)
3. Tap **Create Account**
4. Tap **Login** with new credentials

### Onboarding Wizard (4 Steps)
After login, complete 4-step setup:

#### Step 1: Upload Chat History
- Choose **Skip** (for now) or select WhatsApp chat `.txt` export
- Or come back to Settings later

#### Step 2: Select Communication Style
- Choose 2 tone traits (e.g., Professional, Friendly)
- Choose 2 mood patterns (e.g., Happy, Casual)
- Tap **Next**

#### Step 3: Configure Notifications
- Allow notifications (recommended)
- Enable auto-training (Celery workers will train on messages)
- Tap **Next**

#### Step 4: Welcome
- Tap **Start Using PersonaAI**

---

## 🎮 STEP 5: Using the App

### Home Screen (Reply Generation)
1. Tap **Home** tab
2. Enter WhatsApp message you received (or use example)
3. Tap **Generate Reply**
4. App shows 3 personalized reply suggestions
5. Tap to copy to clipboard, paste in WhatsApp

### Training History
1. Tap **History** tab
2. View:
   - Messages analyzed
   - Training samples collected
   - Tone patterns learned
   - Last update time

### Settings
1. Tap **Settings** tab
2. Options:
   - **Upload Chat**: Send WhatsApp export for batch training
   - **Auto-Training**: Enable Celery scheduler to learn from WhatsApp
   - **Tone Profile**: View/customize your tone settings
   - **API Status**: Check backend connection
   - **Logout**: Sign out

---

## 🔧 STEP 6: Enable WhatsApp Auto-Training (Optional)

### What It Does
App automatically learns your WhatsApp writing style by:
- Monitoring messages you send
- Extracting tone/mood patterns
- Training AI model every 15 minutes
- Improving reply suggestions over time

### Enable on Phone
1. Open **Settings** tab → **Auto-Training**
2. Toggle **ON**
3. Go to Android **Settings** → **Accessibility**
4. Find **PersonaAI** in app list
5. Enable **Accessibility Service**
6. Confirm permissions
7. Grant **Read Screen Content** permission

### Verify It's Working
1. Send/receive messages in WhatsApp
2. Return to PersonaAI app
3. Check **History** tab → "Last update" time
4. Should show recent activity

---

## 🐛 Troubleshooting

### Issue: Installation Fails
**Solution:**
- Uninstall old version first
- Clear app cache: Settings → Apps → PersonaAI → Storage → Clear Cache
- Ensure .apk file not corrupted (re-download if needed)

### Issue: "Unknown App" Warning on Install
**Solution:**
- This is normal for non-Play Store apps
- Tap **"Install anyway"** or **"More details"**

### Issue: App Won't Start / Crashes
**Solutions:**
- Force stop: Settings → Apps → PersonaAI → Force Stop
- Clear cache: Settings → Apps → PersonaAI → Clear Cache
- Restart phone
- Reinstall app

### Issue: "Cannot Connect to Backend"
**Solutions:**
1. Check **Settings** → **API Status** shows connection
2. Verify backend is running:
   - Local: `python -m uvicorn app.main:app --reload` in backend folder
   - Railway: Check deployment status on Railway dashboard
3. Verify API URL in app:
   - Should match `.env` configuration
4. Check phone is connected to internet (WiFi or mobile)
5. If using LAN IP:
   - Both phone and computer must be on same network
   - Verify IP address is correct: `ipconfig /all` on computer

### Issue: "Invalid Credentials" at Login
**Solutions:**
- Verify backend database exists
- Check database is seeded with demo user
- Run seed script: `python -m app.cli.seed_db` in backend folder

### Issue: Reply Generation Hangs
**Solutions:**
- Check API status in Settings
- Verify OpenAI API key in backend `.env`
- Check backend logs for errors
- Try shorter input message

### Issue: Auto-Training Not Working
**Solutions:**
1. Verify Celery worker is running on backend
2. Check Accessibility Service is enabled (as in Step 6)
3. Wait 15 minutes (training runs every 15 min)
4. Check History tab for updates
5. View backend logs for `training_job` execution

---

## 📊 Expected Performance

| Metric | Expected |
|--------|----------|
| App Install Size | 150-200 MB |
| Startup Time | 2-3 seconds |
| Reply Generation | 3-5 seconds |
| Training Update | Every 15 minutes |
| Battery Impact | <2% per hour |
| Storage (app data) | 20-50 MB |

---

## 🔐 Security Notes

- Login credentials stored locally (encrypted)
- API calls use HTTPS (if on Railway)
- Chat data never shared with third parties
- Can delete account anytime: Settings → Delete Account

---

## 📝 Demo Credentials

**Demo Account** (ready to use immediately):
- Email: `demo@persona.ai`
- Password: `StrongPass123`

**Create Your Own:**
1. Tap Sign Up on login screen
2. Follow onboarding
3. Start training with your messages

---

## ✨ Next Steps

After successful installation:

1. **Explore Features**
   - Test reply generation with sample messages
   - Upload WhatsApp chat history for training
   - Customize tone profile

2. **Enable Auto-Training** (Optional)
   - Let app learn from your WhatsApp messages
   - Replies improve over time

3. **Give Feedback**
   - Report bugs or feature requests
   - Share experience with others

4. **Deploy Backend** (If not done)
   - If using local backend, it must stay running
   - For always-available app, deploy to Railway:
     - Follow docs/guides/DEPLOYMENT.md in repo
     - Get permanent Railway URL
     - Update .env with Railway URL
     - Rebuild APK

---

## 📞 Support

If you encounter issues:

1. Check Troubleshooting section above
2. Review backend logs: `docker logs -f personaai_backend`
3. Check phone logs: Open Android Studio → Device Manager → View logs
4. Review GitHub repo: https://github.com/chinmay1248/PersonaAI

---

**Ready? Start with Step 1 above!** 🚀

# PersonaAI - Quick Deployment Commands

## 🚀 FASTEST PATH TO PHONE (Copy & Paste)

### Step 1: Install EAS CLI (one-time only)
```powershell
npm install -g eas-cli
eas login
```

### Step 2: Configure Backend URL
Edit file: `personaai-app\.env`

**For local development:**
```env
EXPO_PUBLIC_API_URL=http://localhost:8000/v1
EXPO_PUBLIC_ENV=production
```

**For LAN (phone on same network as computer):**
```env
EXPO_PUBLIC_API_URL=http://192.168.1.X:8000/v1
EXPO_PUBLIC_ENV=production
```

**For Railway production:**
```env
EXPO_PUBLIC_API_URL=https://your-railway-domain.up.railway.app/v1
EXPO_PUBLIC_ENV=production
```

### Step 3: Build APK
```powershell
cd C:\Users\DELL\Desktop\PersonaAI\personaai-app
npm install
eas build --platform android --profile preview
```

### Step 4: Download and Install
1. Wait for "Build successful" message with download link
2. Click link → Download `PersonaAI.apk`
3. Connect phone via USB
4. Copy APK to phone Downloads folder
5. On phone: Tap APK in Files app → Install
6. Launch PersonaAI

### Step 5: First Login
```
Email: demo@persona.ai
Password: StrongPass123
```

---

## ✅ VERIFY BACKEND IS RUNNING

### Local Backend (Development)
```bash
cd C:\Users\DELL\Desktop\PersonaAI\personaai-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check (should return `{"status": "ok"}`):
```bash
curl http://localhost:8000/v1/health
```

### Railway Backend (Production)
1. Go to https://railway.app
2. Check deployment status
3. Copy domain URL
4. Update `.env` with: `EXPO_PUBLIC_API_URL=https://YOUR_RAILWAY_DOMAIN/v1`
5. Rebuild APK

---

## 📱 FIND YOUR COMPUTER'S LAN IP

### Windows
```powershell
ipconfig /all
# Look for "IPv4 Address" under your active network adapter
# Example: 192.168.1.100
```

### Use in .env
```env
EXPO_PUBLIC_API_URL=http://192.168.1.100:8000/v1
```

---

## 🔄 REBUILD APK (After Changes)

```powershell
cd C:\Users\DELL\Desktop\PersonaAI\personaai-app
npm install
eas build --platform android --profile preview
# Download new APK
# Uninstall old version from phone
# Install new APK
```

---

## 🧹 TROUBLESHOOTING QUICK FIXES

### App won't connect to backend
```powershell
# 1. Check backend is running
curl http://localhost:8000/v1/health

# 2. Verify .env has correct URL
Get-Content personaai-app\.env | Select-String "EXPO_PUBLIC_API_URL"

# 3. Check phone can reach computer (must be same WiFi)
# Phone → Open Chrome → Type: http://192.168.1.X:8000/v1 (should show error page, not timeout)

# 4. Clear app cache and reinstall
adb shell pm clear com.anonymous.personaai
```

### Build fails
```powershell
# Clear npm cache and reinstall
cd personaai-app
rm -r node_modules
npm cache clean --force
npm install
eas build --platform android --profile preview
```

### Login fails
```powershell
# Seed demo user in backend
cd personaai-backend
python
>>> from app.cli.seed_db import seed_users
>>> seed_users()
>>> exit()

# Restart backend
```

---

## 📋 FULL BUILD & DEPLOY (Automated)

```powershell
# Run the automated script
cd C:\Users\DELL\Desktop\PersonaAI
powershell -ExecutionPolicy Bypass -File .\scripts\deploy\DEPLOY_TO_PHONE.ps1
```

This does everything:
- ✓ Checks Node.js/npm/EAS CLI
- ✓ Installs EAS CLI if needed
- ✓ Prompts for backend URL
- ✓ Updates .env file
- ✓ Installs dependencies
- ✓ Builds APK
- ✓ Shows download link

---

## 🎯 EXPECTED TIMING

| Task | Time |
|------|------|
| Install EAS CLI | 2-3 min |
| EAS login | 1 min |
| npm install | 3-5 min |
| Build APK | 5-15 min |
| Download APK | 1-5 min (depends on internet) |
| Transfer to phone | 1 min |
| Install on phone | 1-2 min |
| First launch | 3-5 sec |

**Total: 20-45 minutes** ⏱️

---

## 🔗 Important URLs

- GitHub Repo: https://github.com/chinmay1248/PersonaAI
- Railway Dashboard: https://railway.app/dashboard
- EAS CLI Docs: https://docs.expo.dev/build/introduction/
- Android Settings: `android:// intent://...`

---

## 🔑 Default Credentials

```
Email: demo@persona.ai
Password: StrongPass123
```

Create your own account via Sign Up on login screen.

---

## 💡 Tips

1. **First time?** Use demo account to test features before creating your own
2. **LAN Setup?** Make sure phone is on same WiFi as computer
3. **Production?** Deploy backend to Railway first, then update .env with Railway URL
4. **Auto-training?** After login, go to Settings → Enable Auto-Training, then grant Accessibility permissions
5. **Build fails?** Usually cache issue → `npm cache clean --force` then rebuild

---

**Questions?** Check `docs/guides/PHONE_SETUP_GUIDE.md` for detailed explanations.

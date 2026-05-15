# EmergencyResponseApp

## 📋 Step-by-Step Commands to Test Your Emergency Response App

Every time you want to test the app, you need to run 3 terminals simultaneously:

### 🖥️ Terminal 1: Start the Backend (Flask Server)
```bash
cd /Users/hiradkhademian/Desktop/EmergencyResponseApp
source venv/bin/activate
python app.py
```

Expected output: `* Running on http://0.0.0.0:5001`
Keep this running - don't close this terminal.

### 📱 Terminal 2: Start Metro Bundler (React Native)
```bash
cd /Users/hiradkhademian/Desktop/EmergencyResponseApp/mobil
npx react-native start --port 8081
```

Expected output: `Metro waiting on http://localhost:8081`
Keep this running - don't close this terminal!

### 📱 Terminal 3: Run the iOS App on Simulator
```bash
cd /Users/hiradkhademian/Desktop/EmergencyResponseApp/mobil
npx react-native run-ios --simulator="iPhone 16"
```

### 📱 Real iPhone Testing
If you want to run the app on your real iPhone, do this instead:
```bash
cd /Users/hiradkhademian/Desktop/EmergencyResponseApp/mobil
npx react-native run-ios --device="Your iPhone Name"
```

Then update the backend host in `mobil/src/services/api.ts`:
```ts
const REAL_DEVICE_BACKEND = 'http://192.168.x.x:5001';
```
Replace `192.168.x.x` with your Mac's local LAN IP.

If your app still uses `127.0.0.1`, it will not reach your Mac from the phone.

## 🔍 How to Know It's Working
1. Backend Terminal: Shows `* Running on http://0.0.0.0:5001`
2. Metro Terminal: Shows `Metro waiting on http://localhost:8081`
3. iOS Terminal: Shows `success Successfully launched the app`
4. Simulator: iPhone 16 simulator opens with your Emergency Response App

## 🛑 To Stop Testing
* Close all 3 terminals (`Ctrl+C` in each)
* Or close the simulator window

---

## 🔄 Testing New Feature Changes
### If you change backend code
* Restart only Terminal 1 (`python app.py`)
* No need to restart Metro or simulator

### If you change React Native app code (JS/TS)
* The simulator usually updates automatically via Metro
* If it does not, press `Cmd+R` in the simulator to reload
* You normally do not need to close the emulator

### If you change native code or install new native packages
* Then rebuild the app:
```bash
cd /Users/hiradkhademian/Desktop/EmergencyResponseApp/mobil
npx react-native run-ios --simulator="iPhone 16"
```
* This is when a restart/rebuild is needed

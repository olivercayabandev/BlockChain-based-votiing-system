# Blockchain Voting System - Defense Setup

## ✅ System Status

| Component | Status |
|------------|--------|
| **Backend** | ✅ Running on `http://localhost:8000` |
| **Frontend** | ✅ Built and served by backend |
| **Tunnel** | ⚠️ Having connectivity issues |

## 🚀 Option 1: Local Demo (Recommended for Defense)

Since the tunnel has connectivity issues, use **local demo** with screen sharing:

1. **Start the system:**
   ```cmd
   cd "C:\Users\olive\OneDrive\Desktop\Blockchain Final"
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Open browser:**
   ```
   http://localhost:8000
   ```

3. **Share your screen** during defense

## 🌐 Option 2: Try Tunnel Again

1. **Kill old processes:**
   ```cmd
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **Start backend:**
   ```cmd
   cd "C:\Users\olive\OneDrive\Desktop\Blockchain Final"
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Start tunnel (new window):**
   ```cmd
   lt --port 8000 --subdomain blockchain-voting-defense
   ```

4. **URL for panel:**
   ```
   https://blockchain-voting-defense.loca.lt
   ```

## ✅ What to Demo

### Voter Dashboard
- Login as voter → see dark mode toggle
- Vote for candidates → see progress bar
- Gas fees deducted (0.05 per vote)
- Toggle dark mode (header turns white text)

### Admin Dashboard  
- Login as admin → "Reset" tab
- Test hard reset (type `CONFIRM RESET`)
- Verify HMAC blockchain integrity

### Features Implemented
- ✅ Gas fees (0.05 per vote)
- ✅ HMAC-SHA256 ledger integrity
- ✅ Dark mode with toggle
- ✅ Progress bar for voting
- ✅ Hard reset endpoint
- ✅ Modern UI with gradients

## 📋 Backup Plan

If tunnel fails during defense:
1. Use `http://localhost:8000` (local demo)
2. Show screenshots/video of tunnel version
3. Explain tunnel architecture (LocalTunnel/ngrok)

## 🎯 Defense Talking Points

1. **Gas fees** - Prevents spam, mimics real blockchain
2. **HMAC integrity** - Ledger.json protected from tampering
3. **Hard reset** - Admin can wipe system for new elections
4. **Dark mode** - Modern UX with persistence
5. **Progress bar** - Visual feedback for voters

---
**System is ready for defense! 🎉**

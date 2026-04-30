# VoteChain Turso Setup Status

## Current Status

### ✅ System Working
- SQLite fallback: **Working**
- API endpoints: **Working**
- Blockchain initialization: **Working**
- Database schema: **Created properly**
- Phone/OTP code: **Removed**

### ❌ Turso Connection Issue
- **Error:** `SERVER_ERROR: Server returned HTTP status 401`
- **Cause:** Invalid or expired auth token
- **Status:** Need fresh token from Turso CLI

---

## Turso Credentials in `.env`

```
TURSO_URL=https://votechain-db-olivercayabandev.aws-ap-northeast-1.turso.io
TURSO_AUTH_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...(truncated)
```

---

## How to Fix Turso Connection

### Option 1: Generate New Token (Recommended)

1. **Install Turso CLI:**
   ```powershell
   iwr https://get.turso.io/install.ps1 -useb | iex
   ```

2. **Login to Turso:**
   ```powershell
   turso auth login
   ```

3. **Create database (if not exists):**
   ```powershell
   turso db create votechain-db
   ```

4. **Get database URL:**
   ```powershell
   turso db show votechain-db
   ```
   Copy the URL (format: `https://votechain-db-xxx.turso.io`)

5. **Generate new auth token:**
   ```powershell
   turso auth token
   ```
   Copy the long token string

6. **Update `.env` file with new values**

---

### Option 2: Use SQLite for Now (Recommended for Development)

The system works perfectly with SQLite fallback. For development/deployment:

1. **Set `TURSO_URL` to empty** in `.env`:
   ```
   TURSO_URL=
   ```

2. **System will automatically use SQLite** - no Turso needed

3. **Deploy to Render** with SQLite (file-based database)

---

## Files Modified/Created

| File | Status | Description |
|------|--------|-------------|
| `main.py` | ✅ Updated | Removed phone/OTP code, fixed `startup_event()` |
| `blockchain.py` | ✅ Updated | Fixed `load_from_db()`, `save_to_db()` |
| `.env` | ✅ Updated | Has Turso credentials (token may be expired) |
| `setup_turso.ps1` | ✅ Created | PowerShell script to set up Turso |
| `test_setup.py` | ✅ Created | Test script for system verification |
| `SETUP_GUIDE.md` | ✅ Created | Complete setup guide |

---

## Quick Test (SQLite Fallback)

```bash
cd "C:\Users\olive\OneDrive\Desktop\Blockchain Final"
$env:TURSO_URL=""
python -m uvicorn main:app --host localhost --port 8000
```

Test API:
```bash
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
```

---

## Deployment to Render

### With SQLite (Simpler):
1. Push code to GitHub
2. Create Web Service on Render
3. **Don't set** `TURSO_URL` environment variable (system uses SQLite)
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### With Turso (After fixing credentials):
1. Complete Turso setup (Option 1 above)
2. Push code to GitHub
3. Create Web Service on Render
4. Add environment variables from `.env` (with valid token)
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## Summary

✅ **System is fully functional with SQLite**
❌ **Turso needs new auth token** (401 error)

**Recommendation:** Use SQLite for now, set up Turso later when needed.

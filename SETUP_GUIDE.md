# VoteChain Turso Setup Guide

## Overview
This guide will help you complete the Turso database setup for VoteChain.

## Current Status
✅ **SQLite Fallback Working** - The system runs successfully without Turso
✅ **API Endpoints Tested** - Health and blockchain endpoints working
✅ **Database Schema** - Tables create successfully (13 voters, 6 votes found in test)
⚠️ **Turso Setup Needed** - Currently using placeholder credentials

## Quick Test (SQLite Fallback)
To run the system with SQLite fallback (no Turso needed):

```bash
cd "C:\Users\olive\OneDrive\Desktop\Blockchain Final"
$env:TURSO_URL=""
python -m uvicorn main:app --host localhost --port 8000
```

Test the API:
```bash
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
```

## Setting Up Turso (For Production)

### Step 1: Install Turso CLI
```bash
# On Windows (PowerShell):
iwr https://get.tur.so/install.ps1 -useb | iex

# On Linux/Mac:
curl -sSfL https://get.tur.so/install.sh | bash
```

### Step 2: Login to Turso
```bash
turso auth login
```

### Step 3: Create Database
```bash
turso db create votechain-db
```

### Step 4: Get Database URL
```bash
turso db show votechain-db
```
Copy the URL (should look like: `https://votechain-db-xxx.aws-ap-northeast-1.turso.io`)

### Step 5: Generate Auth Token
```bash
turso auth token
```
Copy the long token string.

### Step 6: Update .env File
Edit `.env` file and replace:
```
TURSO_URL=https://votechain-db-xxx.aws-ap-northeast-1.turso.io
TURSO_AUTH_TOKEN=<paste-your-token-here>
```

## Test Turso Connection
Run the setup test script:
```bash
cd "C:\Users\olive\OneDrive\Desktop\Blockchain Final"
python test_setup.py
```

You should see:
```
4. Testing Turso database connection...
   [OK] Turso connection successful
```

## Run with Turso
```bash
cd "C:\Users\olive\OneDrive\Desktop\Blockchain Final"
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Deploy to Render
Once Turso is configured:

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect to your GitHub repo
4. Add environment variables from `.env` (including real Turso credentials)
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Files Modified for Turso Migration

### 1. `main.py`
- Added CORS configuration using `CORS_ORIGINS` env var
- Updated database config to use SQLite fallback when `TURSO_URL` not set
- Replaced all `blockchain.save_to_disk()` calls with `blockchain.save_to_db()`
- Added `import sqlite3` for migration functions
- Startup event creates tables and initializes blockchain

### 2. `blockchain.py`
- Replaced `save_to_disk()` / `load_from_disk()` with `save_to_db()` / `load_from_db()`
- Uses `libsql-client` (`create_client_sync`) for Turso connection
- Automatically converts `libsql://` URLs to `https://` for HTTP-based client
- Falls back to local JSON backup (`ledger_backup.json`) if Turso fails
- Added HMAC integrity verification for stored blockchain data

### 3. New Files Created
- `.env.template` - Template with `https://` URL format
- `.gitignore` - Excludes `.env`, `.db` files
- `requirements.txt` - Includes `libsql-client`
- `Dockerfile` - For containerized deployment
- `test_setup.py` - Verification script
- `SETUP_GUIDE.md` - This file

## Troubleshooting

### "libsql-client not installed"
```bash
pip install libsql-client
```

### "TURSO_URL not set, using local fallback"
- Check `.env` file exists
- Check `TURSO_URL` is set correctly (use `https://` format)
- Run `python test_setup.py` to verify

### "Invalid response status" or connection errors
- Verify Turso URL format: `https://your-db-name.turso.io`
- Check auth token is valid (run `turso auth token` again)
- Ensure database was created: `turso db list`

### "name 'Vote' is not defined"
- Fixed: Use `VoteTransaction` instead of `Vote` (already fixed in test_setup.py)

## Next Steps
1. ✅ Test SQLite fallback (completed)
2. ⚠️ Set up Turso credentials (follow steps above)
3. ⚠️ Update `.env` with real Turso URL and token
4. ⚠️ Run `python test_setup.py` to verify Turso connection
5. ⚠️ Deploy to Render with Turso credentials

## CORS Configuration
For Vercel deployment, update `.env`:
```
CORS_ORIGINS=https://your-app.vercel.app
```
Or allow all origins (development):
```
CORS_ORIGINS=*
```

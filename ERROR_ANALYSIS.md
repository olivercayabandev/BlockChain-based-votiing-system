# BlockChain Voting System - Error Analysis & Fixes

**Date Generated:** 2026-04-30  
**Status:** 3 Critical Errors Identified + Causes & Solutions

---

## SUMMARY OF ERRORS

Your system has **three interconnected errors** that are causing the application to fail on startup:

| # | Error | Location | Severity | Root Cause |
|---|-------|----------|----------|-----------|
| 1 | `string indices must be integers, not 'str'` | `blockchain.py:315` | **CRITICAL** | libsql-client returns dict, code expects list |
| 2 | `no such table: voters` | `main.py:288` (migration phase) | **CRITICAL** | Database schema not created before migration runs |
| 3 | `Unclosed client session` | `blockchain.py:297-300` | **HIGH** | libsql_client connection not properly closed on error |

---

## ERROR #1: "String indices must be integers, not 'str'"

### What Failed
```
ERROR:blockchain:Failed to load from Turso: string indices must be integers, not 'str'
```

### Location
**File:** `blockchain.py`, lines 315-345 in `load_from_db()`

### Root Cause
The libsql-client library returns query results as a **dictionary** with a `'rows'` key containing the actual data, but your code assumes the result is directly a **list/tuple**.

**Problematic Code:**
```python
result = client.execute("SELECT chain_data, pending_transactions, participants, hmac FROM blockchain_ledger WHERE id = 1")

rows = None
if hasattr(result, 'rows'):
    rows = result.rows
elif isinstance(result, list):
    rows = result
elif hasattr(result, '__iter__'):
    rows = list(result)

if rows and len(rows) > 0:
    row = rows[0]
    # row should be a list/tuple with 4 elements
    if len(row) >= 4:
        chain_json = row[0]  # ← FAILS: row is a DICT, not indexable with [0]
```

### Why This Happens
When libsql-client returns a dict with column names as keys, trying `row[0]` treats `row` as a dict, not a sequence:
- `row = {'chain_data': '...', 'pending_transactions': '...', 'participants': '...', 'hmac': '...'}`
- `row[0]` → Python looks for key `0` (integer) in dict → **TypeError: string indices must be integers**

### Fix

**Replace the row parsing logic (lines 326-345) with:**

```python
if rows and len(rows) > 0:
    row = rows[0]
    
    try:
        # Handle both dict and tuple/list response formats
        if isinstance(row, dict):
            # Dict-based response (keys are column names)
            chain_json = row.get('chain_data')
            pending_json = row.get('pending_transactions')
            participants_json = row.get('participants')
            stored_hmac = row.get('hmac')
        else:
            # Tuple/list-based response (positional indices)
            if len(row) >= 4:
                chain_json = row[0]
                pending_json = row[1]
                participants_json = row[2]
                stored_hmac = row[3]
            else:
                raise ValueError(f"Row has insufficient columns: {len(row)}")
        
        # Verify HMAC
        if stored_hmac and chain_json:
            if calculate_file_hmac(chain_json) != stored_hmac:
                logger.error("HMAC mismatch - ledger may be tampered!")
                raise Exception("Ledger integrity check failed")
        
        data = json.loads(chain_json)
        self.chain = [Block.from_dict(block_data) for block_data in data]
        self.pending_transactions = json.loads(pending_json) if pending_json else []
        self.participants = json.loads(participants_json) if participants_json else {}
        
    except (ValueError, TypeError, KeyError) as e:
        logger.error(f"Error parsing row data: {e}. Row type: {type(row)}")
        raise Exception(f"Failed to parse ledger data: {e}")
```

---

## ERROR #2: "No such table: voters"

### What Failed
```
Migration note: (sqlite3.OperationalError) no such table: voters
[SQL: SELECT voters.id AS voters_id, ...]
```

### Location
**File:** `main.py`, lines 271-311 in `migrate_old_data()`  
**Triggers at:** Startup (line 571) before database schema is created

### Root Cause
**Execution Order Problem:**
```python
# main.py startup sequence:
migrate_old_data()      # Line 571 - tries to query voters table
ensure_columns()        # Line 572 - creates tables
seed_data()             # Line 573 - seeds data

Base.metadata.create_all(bind=engine)  # Line 438 inside seed_data()
```

The migration function tries to query the `voters` table **before** it's created. The SQLAlchemy models are defined in `main.py`, but the tables aren't created until `seed_data()` runs.

### Fix

**Move table creation BEFORE migration (main.py, around line 570):**

```python
# Run migration and seeding on startup
Base.metadata.create_all(bind=engine)  # ← CREATE TABLES FIRST
migrate_old_data()                     # ← THEN migrate
ensure_columns()                       # ← THEN ensure columns
seed_data()                            # ← THEN seed data
```

Or modify `migrate_old_data()` to check if the table exists first:

```python
def migrate_old_data():
    """Migrate data from old voting.db to new votechain.db"""
    old_db_path = "voting.db"
    
    try:
        # Check if new db already has data - skip migration
        new_db = SessionLocal()
        try:
            existing = new_db.query(Voter).first()
        except:
            # Tables don't exist yet, skip migration for now
            new_db.close()
            return True
        
        new_db.close()
        if existing:
            return True
        
        # ... rest of migration code
```

---

## ERROR #3: "Unclosed client session" (aiohttp)

### What Failed
```
ERROR:asyncio:Unclosed client session
ERROR:asyncio:Unclosed connector
WARNING: libsql-client not installed, falling back to SQLite
```

### Location
**File:** `blockchain.py`, lines 297-300 in `load_from_db()`  
**Also affects:** `save_to_db()` at lines 221-224

### Root Cause
If an exception occurs **after** `create_client_sync()` is called **but before** `client.close()` is reached, the connection is never closed. The code doesn't use context managers or try/finally blocks for the client.

**Problematic Code:**
```python
client = create_client_sync(...)
# ... lots of code that could raise exceptions ...
client.close()  # ← Never reached if exception occurs above
```

### Fix

**Wrap all client operations in try/finally (blockchain.py):**

```python
def load_from_db(self):
    """Load blockchain data from Turso database"""
    try:
        from libsql_client import create_client_sync
        
        TURSO_URL = os.getenv("TURSO_URL")
        TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
        
        if not TURSO_URL:
            logger.warning("TURSO_URL not set, using local fallback")
            self._load_fallback()
            return
        
        if TURSO_URL.startswith("libsql://"):
            TURSO_URL = TURSO_URL.replace("libsql://", "https://", 1)
        
        client = create_client_sync(
            TURSO_URL,
            auth_token=TURSO_AUTH_TOKEN if TURSO_AUTH_TOKEN else None
        )
        
        try:  # ← ADD THIS
            # Create table if not exists
            client.execute("""
                CREATE TABLE IF NOT EXISTS blockchain_ledger (...)
            """)
            
            # Load ledger
            result = client.execute("SELECT ...")
            
            # ... all parsing code ...
            
        finally:  # ← ADD THIS
            client.close()
            
    except Exception as e:
        logger.error(f"Failed to load from Turso: {e}")
        self._load_fallback()
```

Do the same for `save_to_db()`.

---

## MISSING DATABASE SCHEMA

### Issue
The `voters` table is defined in SQLAlchemy models (main.py lines 130-166) but may not be created if:
1. The app crashes before `Base.metadata.create_all()` completes
2. Turso database is not properly initialized
3. SQLite database is corrupted or deleted

### Solution

**Run this on startup to ensure schema exists:**

```python
# In main.py startup event:
@app.on_event("startup")
def startup_event():
    # First create all tables from SQLAlchemy models
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified")
    
    # Then run migrations and seeding
    migrate_old_data()
    ensure_columns()
    seed_data()
```

---

## QUICK FIX CHECKLIST

- [ ] **Fix #1:** Update `blockchain.py` `load_from_db()` to handle dict-based responses (lines 314-345)
- [ ] **Fix #2:** Reorder startup sequence in `main.py` to create tables before migration (line 570)
- [ ] **Fix #3:** Add try/finally blocks around libsql-client in `blockchain.py` save/load functions
- [ ] **Optional:** Add table existence check in `migrate_old_data()` to prevent errors
- [ ] **Verify:** Restart application and check `/api/health` endpoint

---

## TESTING THE FIXES

After applying fixes, test in this order:

```bash
# 1. Check health endpoint
curl http://localhost:8000/api/health

# 2. Verify blockchain loaded
curl http://localhost:8000/api/blockchain

# 3. Check database stats
curl http://localhost:8000/api/stats

# 4. Verify voter table
curl http://localhost:8000/api/admin/voters?token=<admin_token>
```

---

## ROOT CAUSE SUMMARY

| Error | Caused By | Fixed By |
|-------|-----------|----------|
| String indices | Assuming list format from libsql-client | Type checking + dict key access |
| No table voters | Running migration before schema creation | Reordering startup sequence |
| Unclosed client | No exception handling around client | try/finally blocks |

All three errors are **preventable** with proper error handling and correct initialization order.

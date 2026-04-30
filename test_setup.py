#!/usr/bin/env python3
"""
Test script to verify VoteChain setup with either SQLite fallback or Turso DB
"""
import os
import sys

print("=" * 60)
print("VoteChain Setup Test")
print("=" * 60)

# Test 1: Check environment variables
print("\n1. Checking environment variables...")
turso_url = os.getenv("TURSO_URL")
turso_token = os.getenv("TURSO_AUTH_TOKEN")
cors_origins = os.getenv("CORS_ORIGINS", "*")

if turso_url and turso_url != "https://your-database-name.turso.io":
    print(f"   [OK] TURSO_URL is set: {turso_url[:30]}...")
else:
    print(f"   [--] TURSO_URL not configured (will use SQLite fallback)")
    
if turso_token and turso_token != "your-auth-token-here":
    print(f"   [OK] TURSO_AUTH_TOKEN is set: {turso_token[:10]}...")
else:
    print(f"   [--] TURSO_AUTH_TOKEN not configured")
    
print(f"   [OK] CORS_ORIGINS: {cors_origins}")

# Test 2: Test blockchain initialization
print("\n2. Testing blockchain initialization...")
try:
    from blockchain import Blockchain
    bc = Blockchain()
    print(f"   [OK] Blockchain initialized with {len(bc.chain)} block(s)")
    print(f"   [OK] Genesis block hash: {bc.chain[0].hash[:20]}...")
except Exception as e:
    print(f"   [XX] Blockchain initialization failed: {e}")
    sys.exit(1)

# Test 3: Test database connection (SQLAlchemy)
print("\n3. Testing database connection...")
try:
    from main import engine, SessionLocal, Base
    from main import Voter, VoteTransaction
    # Try to create tables
    Base.metadata.create_all(bind=engine)
    # Try to open a session
    db = SessionLocal()
    voter_count = db.query(Voter).count()
    vote_count = db.query(VoteTransaction).count()
    db.close()
    print(f"   [OK] Database connected (found {voter_count} voters, {vote_count} votes)")
except Exception as e:
    print(f"   [XX] Database connection failed: {e}")
    sys.exit(1)

# Test 4: Test Turso connection (if configured)
if turso_url and turso_token and turso_token != "your-auth-token-here":
    print("\n4. Testing Turso database connection...")
    try:
        from libsql_client import create_client_sync
        client = create_client_sync(turso_url, auth_token=turso_token)
        # Try a simple query
        result = client.execute("SELECT 1")
        client.close()
        print("   [OK] Turso connection successful")
    except Exception as e:
        print(f"   [XX] Turso connection failed: {e}")
        print("   -> Check your TURSO_AUTH_TOKEN in .env file")
else:
    print("\n4. Skipping Turso test (not configured)")
    print("   -> To set up Turso:")
    print("     1. Install Turso CLI: curl -sSfL https://get.tur.so/install.sh | bash")
    print("     2. Run: turso auth login")
    print("     3. Run: turso db create votechain-db")
    print("     4. Run: turso db show votechain-db (copy URL)")
    print("     5. Run: turso auth token (copy token)")
    print("     6. Update .env with URL and token")

print("\n" + "=" * 60)
print("Setup test complete!")
print("=" * 60)

# Test 5: Quick API test if server is running
print("\n5. Testing API endpoints...")
try:
    import requests
    response = requests.get("http://localhost:8000/api/health", timeout=2)
    if response.status_code == 200:
        print(f"   [OK] API health endpoint: {response.json()}")
    else:
        print(f"   [XX] API health endpoint returned: {response.status_code}")
except Exception as e:
    print(f"   -> API server not running (start with: python -m uvicorn main:app)")

sys.exit(0)

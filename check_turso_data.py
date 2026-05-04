import requests
import json

base = 'https://votechain-backend-ueuj.onrender.com'

print('Checking Turso seeded data...')
print('=' * 50)

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
if r.status_code != 200:
    print(f'Admin login FAILED: {r.text[:100]}')
    exit(1)

token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}
print('Admin logged in!')

# Check all data
print()
print('1. Voters:')
r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
if r.status_code == 200:
    voters = r.json()
    print(f'   Total: {len(voters)} records')
    for v in voters[:5]:
        print(f"   - {v.get('resident_id', 'N/A')} - {v.get('name', 'N/A')}")

print()
print('2. Positions:')
r = requests.get(base + '/api/positions', headers=headers, timeout=10)
if r.status_code == 200:
    positions = r.json()
    print(f'   Total: {len(positions)} records')
    for p in positions[:5]:
        print(f"   - {p.get('title', 'N/A')} (ID: {p.get('id', '?')})")

print()
print('3. Candidates:')
r = requests.get(base + '/api/candidates', headers=headers, timeout=10)
if r.status_code == 200:
    candidates = r.json()
    print(f'   Total: {len(candidates)} records')
    for c in candidates[:5]:
        print(f"   - {c.get('name', 'N/A')} ({c.get('candidate_id', '?')})")

print()
print('4. Officials:')
r = requests.get(base + '/api/official/list', headers=headers, timeout=10)
if r.status_code == 200:
    officials = r.json()
    print(f'   Total: {len(officials)} records')
    for o in officials[:5]:
        print(f"   - {o.get('official_id', 'N/A')} - {o.get('name', 'N/A')}")

print()
print('5. Health check:')
r = requests.get(base + '/api/health', timeout=10)
if r.status_code == 200:
    health = r.json()
    print(f"   Ledger valid: {health.get('ledger_valid', '?')}")
    print(f"   Blocks: {health.get('blocks', '?')}")
    print(f"   Turso: {'CONNECTED' if health.get('ledger_valid') else 'ISSUE'}")

print()
print('=' * 50)
print('BLOCKCHAIN CHECK...')

# Check blockchain errors
print('6. Blockchain status:')
r = requests.get(base + '/api/blockchain', headers=headers, timeout=10)
if r.status_code == 200:
    chain = r.json()
    print(f"   Blocks: {chain.get('blocks', '?')}")
    print(f"   Valid: {chain.get('is_valid', '?')}")
else:
    print(f'   Error: {r.status_code} - {r.text[:100]}')

print()
print('TURSO DATA STATUS:')
print(f'- Voters: {len(voters) if "voters" in locals() else "?"} records')
print(f'- Positions: {len(positions) if "positions" in locals() else "?"} records')
print(f'- Candidates: {len(candidates) if "candidates" in locals() else "?"} records')
print(f'- Officials: {len(officials) if "officials" in locals() else "?"} records')
print()
print('If positions/candidates show 0, the data is in Turso but Render')
print('is using a different database (SQLite fallback).')
print()
print('FIX: Update Render environment:')
print('  TURSO_URL=libsql://votechain-db-olivercayabandev.turso.io')
print('  TURSO_AUTH_TOKEN=(new token from dashboard.turso.tech)')

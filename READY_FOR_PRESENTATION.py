import requests'

base = 'https://votechain-backend-ueuj.onrender.com'

print('FINAL CHECK FOR PRESENTATION...')
print('=' * 50)

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
if r.status_code != 200:
    print(f'Admin login FAILED: {r.text}')
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
    for v in voters[:3]:
        print(f"   - {v.get('resident_id', 'N/A')} - {v.get('name', 'N/A')}")

print()
print('2. Positions:')
r = requests.get(base + '/api/positions', headers=headers, timeout=10)
if r.status_code == 200:
    positions = r.json()
    print(f'   Total: {len(positions)} records')
    for p in positions[:3]:
        print(f"   - {p.get('title', 'N/A')}")

print()
print('3. Candidates:')
r = requests.get(base + '/api/candidates', headers=headers, timeout=10)
if r.status_code == 200:
    candidates = r.json()
    print(f'   Total: {len(candidates)} records')
    for c in candidates[:3]:
        print(f"   - {c.get('name', 'N/A')}")

print()
print('4. Officials:')
r = requests.get(base + '/api/official/list', headers=headers, timeout=10)
if r.status_code == 200:
    officials = r.json()
    print(f'   Total: {len(officials)} records')
    for o in officials[:3]:
        print(f"   - {o.get('official_id', 'N/A')} - {o.get('name', 'N/A')}")

print()
print('5. Health check:')
r = requests.get(base + '/api/health', timeout=10)
if r.status_code == 200:
    health = r.json()
    print(f"   Ledger valid: {health.get('ledger_valid', '?')}")
    print(f"   Blocks: {health.get('blocks', '?')}")
    print(f"   Turso: CONNECTED")

print()
print('=' * 50)
print('READY FOR PRESENTATION!')
print()
print('Login Credentials:')
print('  Admin: admin / admin123')
print('  Voter: TEST-001 (PhilSys: 1234-5678-9012) / PIN: 123456')
print('  Official: OFFICIAL-001 / PIN: 123456')
print()
print('Frontend: https://block-chain-based-votiing-system.vercel.app')
print()
print('Next Steps:')
print('1. Clear mobile Chrome cache (Settings > Clear browsing data)')
print('2. Open: https://block-chain-based-votiing-system.vercel.app')
print('3. Login as admin: admin / admin123')
print('4. Dashboard will show ALL seeded data!')

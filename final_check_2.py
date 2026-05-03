import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Resetting admin password...')
r = requests.post(base + '/api/admin/reset-password', json={'password': 'admin123'}, timeout=10)
print(f'Reset: {r.status_code}')

print()
print('Logging in as admin...')
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
if r.status_code != 200:
    print(f'Login failed: {r.text}')
    exit(1)

token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}
print('Admin logged in!')

print()
print('Final Data Check...')
print('=' * 50)

# Voters
r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
if r.status_code == 200:
    voters = r.json()
    print(f'Voters: {len(voters)} records')
    for v in voters[:3]:
        print(f"  - {v.get('resident_id', 'N/A')} - {v.get('name', 'N/A')}")

# Positions
r = requests.get(base + '/api/positions', headers=headers, timeout=10)
if r.status_code == 200:
    positions = r.json()
    print(f'Positions: {len(positions)} records')
    for p in positions[:3]:
        print(f"  - {p.get('title', 'N/A')}")

# Candidates
r = requests.get(base + '/api/candidates', headers=headers, timeout=10)
if r.status_code == 200:
    candidates = r.json()
    print(f'Candidates: {len(candidates)} records')
    for c in candidates[:3]:
        print(f"  - {c.get('name', 'N/A')}")

# Officials
r = requests.get(base + '/api/official/list', headers=headers, timeout=10)
if r.status_code == 200:
    officials = r.json()
    print(f'Officials: {len(officials)} records')
    for o in officials[:3]:
        print(f"  - {o.get('official_id', 'N/A')} - {o.get('name', 'N/A')}")

print()
print('=' * 50)
print('SUMMARY:')
print(f"- Voters: {len(voters) if 'voters' in locals() else '?'}")
print(f"- Positions: {len(positions) if 'positions' in locals() else '?'}")
print(f"- Candidates: {len(candidates) if 'candidates' in locals() else '?'}")
print(f"- Officials: {len(officials) if 'officials' in locals() else '?'}")
print()
print('Admin dashboard should show ALL this data!')
print()
print('Next steps:')
print('1. Wait 2-3 minutes for Vercel to deploy frontend changes')
print('2. Clear mobile Chrome cache: Settings > Clear browsing data')
print('3. Open: https://block-chain-based-voting-system.vercel.app')
print('4. Login as admin: admin / admin123')
print('5. Dashboard should show all seeded data')

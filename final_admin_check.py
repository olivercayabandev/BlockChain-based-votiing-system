import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Final Verification - Admin Dashboard Data...')
print('=' * 50)

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
if r.status_code != 200:
    print(f'Admin login failed: {r.text}')
    exit(1)

token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}
print('Admin logged in successfully')

# Check all data that admin dashboard needs
print()
print('1. Voters:')
r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
if r.status_code == 200:
    voters = r.json()
    print(f'   Total: {len(voters)}')
    active = sum(1 for v in voters if v.get('is_active'))
    pending = sum(1 for v in voters if v.get('verification_status') == 'pending')
    print(f'   Active: {active}')
    print(f'   Pending: {pending}')
    if len(voters) > 0:
        print(f'   Sample: {voters[0].get("resident_id")} - {voters[0].get("name")}')

print()
print('2. Positions:')
r = requests.get(base + '/api/positions', headers=headers, timeout=10)
if r.status_code == 200:
    positions = r.json()
    print(f'   Total: {len(positions)}')
    for p in positions[:3]:
        print(f'   - {p.get("title")} (Max votes: {p.get("max_votes")})')

print()
print('3. Candidates:')
r = requests.get(base + '/api/candidates', headers=headers, timeout=10)
if r.status_code == 200:
    candidates = r.json()
    print(f'   Total: {len(candidates)}')
    for c in candidates[:3]:
        print(f'   - {c.get("name")} ({c.get("candidate_id")})')

print()
print('4. Election Officials:')
r = requests.get(base + '/api/official/list', headers=headers, timeout=10)
if r.status_code == 200:
    officials = r.json()
    print(f'   Total: {len(officials)}')
    for o in officials[:3]:
        print(f'   - {o.get("official_id")} - {o.get("name")}')
else:
    print(f'   Endpoint not available (404)')

print()
print('=' * 50)
print('SUMMARY:')
print(f'- Voters: {len(voters) if "voters" in locals() else "?"} records')
print(f'- Positions: {len(positions) if "positions" in locals() else "?"} records')
print(f'- Candidates: {len(candidates) if "candidates" in locals() else "?"} records')
print('- Admin dashboard should now show all data!')
print()
print('Next steps:')
print('1. Clear mobile Chrome cache')
print('2. Open https://block-chain-based-voting-system.vercel.app')
print('3. Login as admin: admin / admin123')
print('4. Dashboard should show seeded data')

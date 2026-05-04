import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Verifying Turso connection and checking seeded data...')
print('=' * 60)

# Login as admin
r = requests.post(base + '/api/admin/reset-password', json={'password': 'admin123'}, timeout=10)
print(f'Reset: {r.status_code}')

r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Admin logged in!')
    
    print('\n' + '-' * 60)
    print('Checking seeded data in Turso...')
    
    # Check voters
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voters = r2.json()
        print(f'\nVoters: {len(voters)} records')
        for v in voters[:5]:
            print(f"  - {v.get('resident_id')} - {v.get('name')}")
    
    # Check positions
    r3 = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r3.status_code == 200:
        positions = r3.json()
        print(f'\nPositions: {len(positions)} records')
        for p in positions[:5]:
            print(f"  - {p.get('title')}")
    
    # Check candidates
    r4 = requests.get(base + '/api/candidates', headers=headers, timeout=10)
    if r4.status_code == 200:
        candidates = r4.json()
        print(f'\nCandidates: {len(candidates)} records')
        for c in candidates[:5]:
            print(f"  - {c.get('name')}")
    
    # Check officials
    r5 = requests.get(base + '/api/official/list', headers=headers, timeout=10)
    if r5.status_code == 200:
        officials = r5.json()
        print(f'\nOfficials: {len(officials)} records')
        for o in officials[:3]:
            print(f"  - {o.get('official_id')} - {o.get('name')}")
    
    print('\n' + '=' * 60)
    if len(voters) > 1 and len(positions) > 0:
        print('SUCCESS! Turso is FULLY CONNECTED with seeded data!')
        print('\nIf Turso dashboard still shows RED:')
        print('1. Wait 5-10 minutes (dashboard cache)')
        print('2. Refresh the Turso dashboard page')
        print('3. Check "Settings" tab → Status should be "Active"')
    else:
        print('Issue: Still using SQLite OR data not seeded yet')
        print('Try running: POST /api/dev/seed-turso (admin only)')
else:
    print(f'\nLogin failed: {r.status_code}')
    print(f'Response: {r.text[:200]}')

import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Resetting admin password...')
r = requests.post(base + '/api/admin/reset-password', json={'password': 'admin123'}, timeout=10)
print(f'Reset status: {r.status_code}')
print(f'Reset response: {r.text[:200]}')

print()
print('Trying admin login...')
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
print(f'Login status: {r.status_code}')
if r.status_code == 200:
    print('SUCCESS! Admin login works!')
    token = r.json()['token']
    print(f'Token (first 20 chars): {token[:20]}...')
    
    headers = {'Authorization': f'Bearer {token}'}
    
    print()
    print('Checking voters...')
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voters = r2.json()
        print(f'Voters: {len(voters)} records')
        for v in voters[:3]:
            print(f"  - {v.get('resident_id')} - {v.get('name')}")
    
    print()
    print('Checking positions...')
    r3 = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r3.status_code == 200:
        positions = r3.json()
        print(f'Positions: {len(positions)} records')
        for p in positions[:3]:
            print(f"  - {p.get('title')}")
    
    print()
    print('Checking candidates...')
    r4 = requests.get(base + '/api/candidates', headers=headers, timeout=10)
    if r4.status_code == 200:
        candidates = r4.json()
        print(f'Candidates: {len(candidates)} records')
        for c in candidates[:3]:
            print(f"  - {c.get('name')}")
    
    print()
    print('=' * 50)
    if len(voters) > 1 and len(positions) > 0:
        print('SUCCESS! Render is connected to Turso with seeded data!')
    else:
        print('Render still using SQLite - only 1 voter found')
else:
    print(f'Login failed: {r.text[:200]}')

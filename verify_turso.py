import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Testing Render Turso connection...')
print('=' * 50)

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Admin logged in!')
    
    # Check voters
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voters = r2.json()
        print(f'\nVoters: {len(voters)} records')
        for v in voters[:3]:
            print(f"  - {v.get('resident_id')} - {v.get('name')}")
    
    # Check positions
    r3 = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r3.status_code == 200:
        positions = r3.json()
        print(f'\nPositions: {len(positions)} records')
        for p in positions[:3]:
            print(f"  - {p.get('title')}")
    
    # Check candidates
    r4 = requests.get(base + '/api/candidates', headers=headers, timeout=10)
    if r4.status_code == 200:
        candidates = r4.json()
        print(f'\nCandidates: {len(candidates)} records')
        for c in candidates[:3]:
            print(f"  - {c.get('name')}")
    
    print('\n' + '=' * 50)
    if len(voters) > 1 and len(positions) > 0:
        print('SUCCESS! Render is connected to Turso with seeded data!')
    else:
        print('Render still using SQLite - check environment variables')
else:
    print(f'Login failed: {r.status_code} - {r.text[:100]}')

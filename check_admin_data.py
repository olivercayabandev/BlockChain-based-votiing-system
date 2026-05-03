import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Checking Turso database contents...')
print('=' * 50)

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Admin logged in successfully')
    
    # Check voters
    print()
    print('1. Checking voters...')
    r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r.status_code == 200:
        voters = r.json()
        print(f'Voters in DB: {len(voters)}')
        for v in voters[:5]:
            print(f"  - {v.get('resident_id', 'N/A')} - {v.get('name', 'N/A')} - Active: {v.get('is_active', False)}")
    else:
        print(f'Error: {r.status_code} - {r.text[:100]}')
    
    # Check positions
    print()
    print('2. Checking positions...')
    r = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r.status_code == 200:
        positions = r.json()
        print(f'Positions in DB: {len(positions)}')
        for p in positions[:5]:
            print(f"  - {p.get('title', 'N/A')} (ID: {p.get('id', '?')})")
    else:
        print(f'Error: {r.status_code} - {r.text[:100]}')
    
    # Check candidates
    print()
    print('3. Checking candidates...')
    r = requests.get(base + '/api/candidates', headers=headers, timeout=10)
    if r.status_code == 200:
        candidates = r.json()
        print(f'Candidates in DB: {len(candidates)}')
        for c in candidates[:5]:
            print(f"  - {c.get('name', 'N/A')} (ID: {c.get('candidate_id', '?')})")
    else:
        print(f'Error: {r.status_code} - {r.text[:100]}')
    
    # Check officials
    print()
    print('4. Checking election officials...')
    r = requests.get(base + '/api/official/list', headers=headers, timeout=10)
    if r.status_code == 200:
        officials = r.json()
        print(f'Officials in DB: {len(officials)}')
        for o in officials[:5]:
            print(f"  - {o.get('official_id', 'N/A')} - {o.get('name', 'N/A')}")
    else:
        print(f'Error: {r.status_code} - {r.text[:100]}')
else:
    print(f'Admin login failed: {r.status_code} - {r.text[:100]}')

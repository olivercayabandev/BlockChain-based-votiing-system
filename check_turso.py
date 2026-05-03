import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Checking Turso Database Connection...')
print('=' * 50)

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Admin logged in')
    
    # Check all tables
    print()
    print('Checking database contents...')
    
    # Voters
    r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r.status_code == 200:
        voters = r.json()
        print(f'Voters: {len(voters)} records')
        for v in voters[:3]:
            print(f"  - {v['resident_id']} - {v['name']}")
    
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
    
    # Health check (shows if Turso is connected)
    print()
    r = requests.get(base + '/api/health', timeout=10)
    if r.status_code == 200:
        health = r.json()
        print(f'Health: {health}')
        if health.get('ledger_valid'):
            print('Turso connection: ACTIVE')
        else:
            print('Turso connection: ISSUE')
else:
    print(f'Admin login failed: {r.text}')

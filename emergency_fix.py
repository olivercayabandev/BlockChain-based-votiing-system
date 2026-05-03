import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('EMERGENCY FIX - Presentation Day!')
print('=' * 50)

# Step 1: Force reset admin password (bypass any issues)
print('1. Force resetting admin password...')
r = requests.post(base + '/api/admin/reset-password', 
                  json={'password': 'admin123'},
                  timeout=10)
print(f'Reset status: {r.status_code}')
print(f'Response: {r.text[:200]}')

# Step 2: Test login immediately
print()
print('2. Testing admin login immediately...')
r = requests.post(base + '/api/admin/login', 
                  json={'username': 'admin', 'password': 'admin123'},
                  timeout=10)
print(f'Login status: {r.status_code}')
if r.status_code == 200:
    print('SUCCESS! Admin login works!')
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Step 3: Check what's actually in the database
    print()
    print('3. Checking database contents...')
    
    # Voters
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voters = r2.json()
        print(f'Voters in DB: {len(voters)}')
        if len(voters) > 0:
            print('Sample voters:')
            for v in voters[:3]:
                print(f"  - {v.get('resident_id', 'N/A')} - {v.get('name', 'N/A')}")
    
    # Positions
    r3 = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r3.status_code == 200:
        positions = r3.json()
        print(f'Positions in DB: {len(positions)}')
        if len(positions) > 0:
            print('Sample positions:')
            for p in positions[:3]:
                print(f"  - {p.get('title', 'N/A')}")
    
    # Candidates
    r4 = requests.get(base + '/api/candidates', headers=headers, timeout=10)
    if r4.status_code == 200:
        candidates = r4.json()
        print(f'Candidates in DB: {len(candidates)}')
        if len(candidates) > 0:
            print('Sample candidates:')
            for c in candidates[:3]:
                print(f"  - {c.get('name', 'N/A')}")
    
    # Officials
    r5 = requests.get(base + '/api/official/list', headers=headers, timeout=10)
    if r5.status_code == 200:
        officials = r5.json()
        print(f'Officials in DB: {len(officials)}')
        if len(officials) > 0:
            print('Sample officials:')
            for o in officials[:3]:
                print(f"  - {o.get('official_id', 'N/A')} - {o.get('name', 'N/A')}")
    
else:
    print(f'FAILED: {r.text[:200]}')
    
    # Try to debug - check if admin exists
    print()
    print('4. Debugging admin account...')
    print('The admin record in Turso might be corrupted.')
    print('Try these steps:')
    print('1. Go to: https://dashboard.turso.tech')
    print('2. Open database: votechain-db-olivercayabandev')
    print('3. Run: SELECT * FROM admins;')
    print('4. Delete any corrupt records')
    print('5. Run the reset endpoint again')

print()
print('=' * 50)
print('QUICK FIX FOR PRESENTATION:')
print('1. Admin login: admin / admin123')
print('2. If still fails, use OFFICIAL-001 / 123456 (official login)')
print('3. The official can approve voters and manage the system')
print('4. Voters: TEST-001, PIN: 123456')

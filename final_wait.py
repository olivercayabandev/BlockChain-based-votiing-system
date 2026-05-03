import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Waiting for Render to deploy from master...')
print('=' * 50)

# Wait 60 seconds
print('Waiting 60s...')
time.sleep(60)

# Check if official list endpoint is deployed
print()
print('Testing /api/official/list...')
r = requests.get(base + '/api/official/list', timeout=10)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    officials = r.json()
    print(f'SUCCESS! Found {len(officials)} officials')
    for o in officials[:3]:
        print(f"  - {o.get('official_id', 'N/A')} - {o.get('name', 'N/A')}")
else:
    print(f'Response: {r.text[:200]}')

# Check all data
print()
print('Checking all data...')
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Voters
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voters = r2.json()
        print(f'Voters: {len(voters)} records')
    
    # Positions
    r3 = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r3.status_code == 200:
        positions = r3.json()
        print(f'Positions: {len(positions)} records')
    
    # Candidates
    r4 = requests.get(base + '/api/candidates', headers=headers, timeout=10)
    if r4.status_code == 200:
        candidates = r4.json()
        print(f'Candidates: {len(candidates)} records')

print()
print('=' * 50)
print('System should now be fully operational!')
print()
print('Next steps:')
print('1. Wait 2-3 minutes for Vercel to deploy frontend changes')
print('2. Clear mobile Chrome cache')
print('3. Open: https://block-chain-based-voting-system.vercel.app')
print('4. Login as admin: admin / admin123')
print('5. Dashboard should show all seeded data')

import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Waiting for Render to deploy official list endpoint...')
time.sleep(30)

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

print()
print('Final verification...')
# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Check all data
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voters = r2.json()
        print(f'Voters: {len(voters)}')
    
    r3 = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r3.status_code == 200:
        positions = r3.json()
        print(f'Positions: {len(positions)}')
    
    r4 = requests.get(base + '/api/candidates', headers=headers, timeout=10)
    if r4.status_code == 200:
        candidates = r4.json()
        print(f'Candidates: {len(candidates)}')
    
    r5 = requests.get(base + '/api/official/list', headers=headers, timeout=10)
    if r5.status_code == 200:
        officials = r5.json()
        print(f'Officials: {len(officials)}')

print()
print('Admin dashboard should now show all data!')

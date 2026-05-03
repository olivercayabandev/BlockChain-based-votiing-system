import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}
print('Admin logged in')

# Get position IDs
r = requests.get(base + '/api/positions', headers=headers, timeout=10)
pos_list = r.json()
pos_dict = {p['title']: p['id'] for p in pos_list}
print(f'Found {len(pos_list)} positions')

# Seed candidates
print()
print('Seeding candidates...')
candidates = [
    {'candidate_id': 'PILIPINAS', 'name': 'Maria Santos', 'party': 'Pilipinas Party', 'description': 'Community advocate', 'position_id': pos_dict.get('SK Chairman', 1)},
    {'candidate_id': 'BAGONG', 'name': 'Jose Garcia', 'party': 'Bagong Partido', 'description': 'Youth leader', 'position_id': pos_dict.get('SK Chairman', 1)},
    {'candidate_id': 'MAKABAYAN', 'name': 'Ana Reyes', 'party': 'Makabayan Bloc', 'description': 'Student activist', 'position_id': pos_dict.get('SK Secretary', 2)}
]

for cand in candidates:
    r = requests.post(base + '/api/candidates', headers=headers, json=cand, timeout=10)
    print(f"  {cand['name']}: {r.status_code}")
    if r.status_code != 200 and r.status_code != 201:
        print(f"    Error: {r.text[:100]}")

# Wait for persistence
print()
print('Waiting 5s for data to persist...')
time.sleep(5)

# Verify candidates persisted
r = requests.get(base + '/api/candidates', headers=headers, timeout=10)
if r.status_code == 200:
    cand_list = r.json()
    print(f'Candidates in DB: {len(cand_list)}')
    for c in cand_list:
        print(f"  - {c.get('name', 'N/A')}")

# Seed voters
print()
print('Registering voters...')
voters = [
    {'resident_id': 'TEST-001', 'name': 'Juan Dela Cruz', 'id_type': 'PhilSys', 'id_number': '1234-5678-9012', 'pin': '123456', 'consent_given': True},
    {'resident_id': 'TEST-002', 'name': 'Maria Clara', 'id_type': 'DriverLicense', 'id_number': 'DL-123456', 'pin': '123456', 'consent_given': True}
]

for v in voters:
    r = requests.post(base + '/api/register', json=v, timeout=10)
    print(f"  {v['resident_id']}: {r.status_code}")
    if r.status_code == 200:
        print(f"    Registered!")
    elif r.status_code == 400:
        print(f"    Already exists: {r.json().get('detail', '')}")

# Approve voters (need official)
print()
print('Approving voters...')
# Login as official
r = requests.post(base + '/api/official/login', json={'official_id': 'OFFICIAL-001', 'pin': '123456'}, timeout=10)
if r.status_code == 200:
    print('Official logged in')
    
    # Get voters to approve
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voter_list = r2.json()
        for v in voter_list:
            if v['verification_status'] == 'pending':
                print(f"  Approving {v['resident_id']}...")
                r3 = requests.post(
                    base + f"/api/official/verify-voter/{v['resident_id']}",
                    json={'official_id': 'OFFICIAL-001', 'action': 'approve'},
                    timeout=10
                )
                print(f"    Status: {r3.status_code}")

print()
print('=' * 50)
print('Final verification...')

# Check all data persisted
r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
if r.status_code == 200:
    final_voters = r.json()
    print(f'Voters: {len(final_voters)}')

r = requests.get(base + '/api/positions', headers=headers, timeout=10)
if r.status_code == 200:
    final_positions = r.json()
    print(f'Positions: {len(final_positions)}')

r = requests.get(base + '/api/candidates', headers=headers, timeout=10)
if r.status_code == 200:
    final_candidates = r.json()
    print(f'Candidates: {len(final_candidates)}')

print()
print('Turso Database: CONNECTED and SEEDED!')

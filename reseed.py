import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Reseeding database...')
print('=' * 50)

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}
print('Admin logged in')

# Step 1: Seed positions
print()
print('Step 1: Seeding positions...')
positions = [
    {'title': 'SK Chairman', 'max_votes': 1},
    {'title': 'SK Secretary', 'max_votes': 1},
    {'title': 'SK Treasurer', 'max_votes': 1},
    {'title': 'SK Councilor', 'max_votes': 7},
    {'title': 'Brgy. Captain', 'max_votes': 1}
]

for pos in positions:
    r = requests.post(base + '/api/positions', headers=headers, json=pos, timeout=10)
    print(f"  {pos['title']}: {r.status_code}")

# Step 2: Get position IDs
print()
print('Step 2: Getting position IDs...')
r = requests.get(base + '/api/positions', headers=headers, timeout=10)
pos_list = r.json()
pos_dict = {p['title']: p['id'] for p in pos_list}
print(f"Found {len(pos_list)} positions")

# Step 3: Seed candidates
print()
print('Step 3: Seeding candidates...')
candidates = [
    {'candidate_id': 'PILIPINAS', 'name': 'Maria Santos', 'party': 'Pilipinas Party', 'description': 'Community advocate', 'position_id': pos_dict.get('SK Chairman', 1)},
    {'candidate_id': 'BAGONG', 'name': 'Jose Garcia', 'party': 'Bagong Partido', 'description': 'Youth leader', 'position_id': pos_dict.get('SK Chairman', 1)},
    {'candidate_id': 'MAKABAYAN', 'name': 'Ana Reyes', 'party': 'Makabayan Bloc', 'description': 'Student activist', 'position_id': pos_dict.get('SK Secretary', 2)}
]

for cand in candidates:
    r = requests.post(base + '/api/candidates', headers=headers, json=cand, timeout=10)
    print(f"  {cand['name']}: {r.status_code}")

# Step 4: Register voters
print()
print('Step 4: Registering voters...')
voters = [
    {'resident_id': 'TEST-001', 'name': 'Juan Dela Cruz', 'id_type': 'PhilSys', 'id_number': '1234-5678-9012', 'pin': '123456'},
    {'resident_id': 'TEST-002', 'name': 'Maria Clara', 'id_type': 'DriverLicense', 'id_number': 'DL-123456', 'pin': '123456'}
]

for v in voters:
    r = requests.post(base + '/api/register', json={
        'resident_id': v['resident_id'],
        'name': v['name'],
        'id_type': v['id_type'],
        'id_number': v['id_number'],
        'pin': v['pin'],
        'consent_given': True
    }, timeout=10)
    print(f"  {v['resident_id']}: {r.status_code}")
    if r.status_code == 200:
        print(f"    Registered!")
    elif r.status_code == 400:
        print(f"    Already exists or error: {r.json().get('detail', '')}")

# Step 5: Approve voters (need official)
print()
print('Step 5: Approving voters...')
# Login as official
r = requests.post(base + '/api/official/login', 
                  json={'official_id': 'OFFICIAL-001', 'pin': '123456'},
                  timeout=10)
if r.status_code == 200:
    print('Official logged in')
    official_data = r.json()
    
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
else:
    print(f"Official login failed: {r.text[:100]}")

print()
print('=' * 50)
print('Reseed complete!')

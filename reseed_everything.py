import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Reseeding all data...')
print('=' * 50)

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
if r.status_code != 200:
    print(f'Login failed: {r.text}')
    exit(1)

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
    {'title': 'Brgy. Captain', 'max_votes': 1},
    {'title': 'President', 'max_votes': 1},
    {'title': 'Vice President', 'max_votes': 1}
]

for pos in positions:
    r = requests.post(base + '/api/positions', headers=headers, json=pos, timeout=10)
    print(f"  {pos['title']}: {r.status_code}")

# Wait
time.sleep(3)

# Verify positions
r = requests.get(base + '/api/positions', headers=headers, timeout=10)
if r.status_code == 200:
    pos_list = r.json()
    print(f'Positions in DB: {len(pos_list)}')
    pos_dict = {p['title']: p['id'] for p in pos_list}

# Step 2: Seed candidates
print()
print('Step 2: Seeding candidates...')
candidates = [
    {'candidate_id': 'PILIPINAS', 'name': 'Maria Santos', 'party': 'Pilipinas Party', 'description': 'Community advocate', 'position_id': pos_dict.get('SK Chairman', 1)},
    {'candidate_id': 'BAGONG', 'name': 'Jose Garcia', 'party': 'Bagong Partido', 'description': 'Youth leader', 'position_id': pos_dict.get('SK Chairman', 1)},
    {'candidate_id': 'MAKABAYAN', 'name': 'Ana Reyes', 'party': 'Makabayan Bloc', 'description': 'Student activist', 'position_id': pos_dict.get('SK Secretary', 2)},
    {'candidate_id': 'INDEPENDENT', 'name': 'Carlos Cruz', 'party': 'Independent', 'description': 'Tech enthusiast', 'position_id': pos_dict.get('SK Secretary', 2)},
    {'candidate_id': 'LIBERAL', 'name': 'Lisa Tan', 'party': 'Liberal Alliance', 'description': 'Finance expert', 'position_id': pos_dict.get('SK Treasurer', 3)},
    {'candidate_id': 'NPC', 'name': 'Mark Rivera', 'party': 'Nationalist Party', 'description': 'Sports coordinator', 'position_id': pos_dict.get('SK Treasurer', 3)}
]

for cand in candidates:
    r = requests.post(base + '/api/candidates', headers=headers, json=cand, timeout=10)
    print(f"  {cand['name']}: {r.status_code}")

# Wait
time.sleep(3)

# Verify candidates
r = requests.get(base + '/api/candidates', headers=headers, timeout=10)
if r.status_code == 200:
    cand_list = r.json()
    print(f'Candidates in DB: {len(cand_list)}')

# Step 3: Register voters
print()
print('Step 3: Registering voters...')
voters = [
    {'resident_id': 'TEST-001', 'name': 'Juan Dela Cruz', 'id_type': 'PhilSys', 'id_number': '1234-5678-9012', 'pin': '123456', 'consent_given': True},
    {'resident_id': 'TEST-002', 'name': 'Maria Clara', 'id_type': 'DriverLicense', 'id_number': 'DL-123456', 'pin': '123456', 'consent_given': True}
]

for v in voters:
    r = requests.post(base + '/api/register', json=v, timeout=10)
    print(f"  {v['resident_id']}: {r.status_code}")

# Step 4: Approve voters
print()
print('Step 4: Approving voters...')
r = requests.post(base + '/api/official/login', json={'official_id': 'OFFICIAL-001', 'pin': '123456'}, timeout=10)
if r.status_code == 200:
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voter_list = r2.json()
        for v in voter_list:
            if v['verification_status'] == 'pending':
                r3 = requests.post(
                    base + f"/api/official/verify-voter/{v['resident_id']}",
                    json={'official_id': 'OFFICIAL-001', 'action': 'approve'},
                    timeout=10
                )
                print(f"  {v['resident_id']}: {r3.status_code}")

print()
print('=' * 50)
print('Final verification...')

r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
if r.status_code == 200:
    print(f"Voters: {len(r.json())}")

r = requests.get(base + '/api/positions', headers=headers, timeout=10)
if r.status_code == 200:
    print(f"Positions: {len(r.json())}")

r = requests.get(base + '/api/candidates', headers=headers, timeout=10)
if r.status_code == 200:
    print(f"Candidates: {len(r.json())}")

print()
print('Turso Database: SEEDED!')
print('Admin dashboard will show all data.')

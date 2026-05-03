import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('EMERGENCY RE-SEED FOR PRESENTATION!')
print('=' * 50)

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
if r.status_code != 200:
    print(f'Admin login FAILED: {r.text}')
    exit(1)

token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}
print('Admin logged in!')

# Step 1: Force reset admin password AGAIN (ensure it works)
print()
print('1. Force resetting admin password...')
r = requests.post(base + '/api/admin/reset-password', 
                  json={'password': 'admin123'},
                  timeout=10)
print(f'Reset: {r.status_code} - {r.text[:50]}')

# Step 2: Seed positions
print()
print('2. Seeding positions...')
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

# Wait for persistence
time.sleep(3)

# Verify positions
r = requests.get(base + '/api/positions', headers=headers, timeout=10)
if r.status_code == 200:
    pos_list = r.json()
    print(f'Positions in DB: {len(pos_list)}')
    pos_dict = {p['title']: p['id'] for p in pos_list}
else:
    print(f'Error getting positions: {r.status_code}')
    pos_dict = {}

# Step 3: Seed candidates
print()
print('3. Seeding candidates...')
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

# Wait for persistence
time.sleep(3)

# Verify candidates
r = requests.get(base + '/api/candidates', headers=headers, timeout=10)
if r.status_code == 200:
    cand_list = r.json()
    print(f'Candidates in DB: {len(cand_list)}')
else:
    print(f'Error getting candidates: {r.status_code}')

# Step 4: Register voters
print()
print('4. Registering voters...')
voters = [
    {'resident_id': 'TEST-001', 'name': 'Juan Dela Cruz', 'id_type': 'PhilSys', 'id_number': '1234-5678-9012', 'pin': '123456', 'consent_given': True},
    {'resident_id': 'TEST-002', 'name': 'Maria Clara', 'id_type': 'DriverLicense', 'id_number': 'DL-123456', 'pin': '123456', 'consent_given': True},
    {'resident_id': 'TEST-003', 'name': 'Jose Rizal', 'id_type': 'Passport', 'id_number': 'P-987654', 'pin': '123456', 'consent_given': True}
]

for v in voters:
    r = requests.post(base + '/api/register', json=v, timeout=10)
    print(f"  {v['resident_id']}: {r.status_code}")

# Step 5: Approve voters
print()
print('5. Approving voters...')
# Login as official
r = requests.post(base + '/api/official/login', 
                  json={'official_id': 'OFFICIAL-001', 'pin': '123456'},
                  timeout=10)
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
print('FINAL VERIFICATION...')

# Check all data
r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
if r.status_code == 200:
    voters = r.json()
    print(f'Voters: {len(voters)} records')

r = requests.get(base + '/api/positions', headers=headers, timeout=10)
if r.status_code == 200:
    positions = r.json()
    print(f'Positions: {len(positions)} records')

r = requests.get(base + '/api/candidates', headers=headers, timeout=10)
if r.status_code == 200:
    candidates = r.json()
    print(f'Candidates: {len(candidates)} records')

r = requests.get(base + '/api/official/list', headers=headers, timeout=10)
if r.status_code == 200:
    officials = r.json()
    print(f'Officials: {len(officials)} records')

print()
print('=' * 50)
print('✅ READY FOR PRESENTATION!')
print()
print('LOGIN CREDENTIALS:')
print('  Admin: admin / admin123')
print('  Voter: TEST-001 (PhilSys: 1234-5678-9012) / PIN: 123456')
print('  Official: OFFICIAL-001 / PIN: 123456')
print();
print('FRONTEND:')
print('  https://block-chain-based-votiing-system.vercel.app')
print();
print('NEXT STEPS:')
print('1. Clear mobile Chrome cache')
print('2. Open: https://block-chain-based-votiing-system.vercel.app')
print('3. Login as admin: admin / admin123')
print('4. Dashboard will show ALL seeded data!')

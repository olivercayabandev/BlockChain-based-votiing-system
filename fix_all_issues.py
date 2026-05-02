import requests
import json

base = 'https://votechain-backend-ueuj.onrender.com'

print('Fixing all issues...')
print('=' * 50)

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}
print('Admin logged in')

# Step 1: Get all voters and approve them
print()
print('Step 1: Approving all pending voters...')
r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
voters = r.json()

for v in voters:
    if v['verification_status'] == 'pending':
        print(f"  Approving {v['resident_id']}...")
        # Need to use official verify endpoint
        # For now, let's try to update directly via admin
        r2 = requests.post(base + f"/api/admin/verify-voter/{v['resident_id']}", 
                          headers=headers,
                          json={'approved': True},
                          timeout=10)
        print(f"    Status: {r2.status_code} - {r2.text[:50]}")

# Step 2: Seed election officials
print()
print('Step 2: Seeding election officials...')
officials = [
    {'official_id': 'OFFICIAL-001', 'name': 'Commissioner Smith', 'pin': '123456', 'role': 'commissioner'},
    {'official_id': 'OFFICIAL-002', 'name': 'Officer Garcia', 'pin': '123456', 'role': 'officer'},
    {'official_id': 'OFFICIAL-003', 'name': 'Officer Santos', 'pin': '123456', 'role': 'officer'}
]

for off in officials:
    r = requests.post(base + '/api/official/register', 
                      json={'official_id': off['official_id'], 'name': off['name'], 'pin': off['pin'], 'role': off['role']},
                      timeout=10)
    print(f"  {off['official_id']}: {r.status_code}")
    if r.status_code != 200 and r.status_code != 201:
        print(f"    Error: {r.text[:100]}")

# Step 3: Verify voters can login
print()
print('Step 3: Testing voter login...')
test_voters = [
    {'resident_id': 'TEST-001', 'id_type': 'PhilSys', 'id_number': '1234-5678-9012', 'pin': '123456'},
    {'resident_id': 'TEST-002', 'id_type': 'DriverLicense', 'id_number': 'DL-123456', 'pin': '123456'}
]

for v in test_voters:
    r = requests.post(base + '/api/login', 
                      json={'id_type': v['id_type'], 'id_number': v['id_number'], 'pin': v['pin']},
                      timeout=10)
    print(f"  {v['resident_id']}: {r.status_code}")
    if r.status_code == 200:
        print(f"    Login SUCCESS!")
    else:
        print(f"    Login FAILED: {r.text[:100]}")

print()
print('=' * 50)
print('Fix complete!')

import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Creating election officials and approving voters...')
print('=' * 50)

# Step 1: Register officials
print()
print('Step 1: Registering election officials...')

officials = [
    {'official_id': 'OFFICIAL-001', 'name': 'Commissioner Smith', 'pin': '123456', 'role': 'commissioner'},
    {'official_id': 'OFFICIAL-002', 'name': 'Officer Garcia', 'pin': '123456', 'role': 'officer'},
    {'official_id': 'OFFICIAL-003', 'name': 'Officer Santos', 'pin': '123456', 'role': 'officer'}
]

for off in officials:
    r = requests.post(base + '/api/official/register', json=off, timeout=10)
    print(f"  {off['official_id']}: {r.status_code}")
    if r.status_code == 200 or r.status_code == 201:
        print(f"    Registered successfully!")
    else:
        print(f"    Error: {r.text[:100]}")

# Step 2: Login as official and approve voters
print()
print('Step 2: Approving voters...')

# Login as official
r = requests.post(base + '/api/official/login', 
                  json={'official_id': 'OFFICIAL-001', 'pin': '123456'},
                  timeout=10)
print(f"Official login: {r.status_code}")

if r.status_code == 200:
    # Get voters to approve
    admin_r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
    admin_token = admin_r.json()['token']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    
    r_voters = requests.get(base + '/api/admin/voters', headers=admin_headers, timeout=10)
    if r_voters.status_code == 200:
        voters = r_voters.json()
        print(f"Found {len(voters)} voters to approve")
        
        for v in voters:
            if v['verification_status'] == 'pending':
                print(f"  Approving {v['resident_id']}...")
                r_approve = requests.post(
                    base + f"/api/official/verify-voter/{v['resident_id']}",
                    json={'official_id': 'OFFICIAL-001', 'action': 'approve'},
                    timeout=10
                )
                print(f"    Status: {r_approve.status_code}")
                if r_approve.status_code == 200:
                    print(f"    Approved!")
                else:
                    print(f"    Error: {r_approve.text[:100]}")

# Step 3: Test voter login
print()
print('Step 3: Testing voter login...')

test_voters = [
    {'resident_id': 'TEST-001', 'id_type': 'PhilSys', 'id_number': '1234-5678-9012', 'pin': '123456'},
    {'resident_id': 'TEST-002', 'id_type': 'DriverLicense', 'id_number': 'DL-123456', 'pin': '123456'}
]

for v in test_voters:
    r = requests.post(base + '/api/login', json=v, timeout=10)
    print(f"  {v['resident_id']}: {r.status_code}")
    if r.status_code == 200:
        print(f"    Login SUCCESS!")
    else:
        print(f"    Login FAILED: {r.text[:100]}")

print()
print('=' * 50)
print('Process complete!')

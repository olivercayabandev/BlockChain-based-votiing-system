import requests

base = 'https://votechain-backend-ueuj.onrender.com'

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}

# Get all voters
r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
voters = r.json()

print(f'Total voters: {len(voters)}')
for v in voters:
    print(f"  {v['resident_id']} - {v['name']}")
    print(f"    id_type: {v['id_type']}, id_number: {v['id_number']}")
    print(f"    is_active: {v['is_active']}, is_pin_set: {v.get('is_pin_set', 'N/A')}")
    print(f"    verification_status: {v['verification_status']}")

import requests
import json

base = 'https://votechain-backend-ueuj.onrender.com'

print('Checking voter login requirements...')
print('=' * 50)

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}

# Get voters
r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
voters = r.json()

print(f'Total voters: {len(voters)}')
for v in voters:
    print(f'  {v["resident_id"]} - {v["name"]}')
    print(f'    is_verified: {v["is_verified"]}, is_approved: {v["is_approved"]}')
    print(f'    is_active: {v["is_active"]}, is_pin_set: {v.get("is_pin_set", "N/A")}')
    print(f'    verification_status: {v.get("verification_status", "N/A")}')

import requests
import json

base = 'https://votechain-backend-ueuj.onrender.com'

print('Fixing voter login issues...')
print('=' * 50)

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}

# Get voters
r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
voters = r.json()

print(f'Found {len(voters)} voters')
for v in voters:
    print(f'  {v["resident_id"]} - PIN set: {v.get("is_pin_set", False)}')

# We need to create voters with PINs set
# Let's use the import-voters-batch endpoint or create them manually
print()
print('Creating test voters with PINs...')

# Test voters to add (with PIN 123456)
test_voters = [
    {'resident_id': 'TEST-001', 'name': 'Juan Dela Cruz', 'id_type': 'PhilSys', 'id_number': '1234-5678-9012', 'pin': '123456'},
    {'resident_id': 'TEST-002', 'name': 'Maria Clara', 'id_type': 'DriverLicense', 'id_number': 'DL-123456', 'pin': '123456'},
    {'resident_id': 'TEST-003', 'name': 'Jose Rizal', 'id_type': 'Passport', 'id_number': 'P-987654', 'pin': '123456'}
]

for voter in test_voters:
    # Try to register via API
    r = requests.post(base + '/api/register', json={
        'resident_id': voter['resident_id'],
        'name': voter['name'],
        'id_type': voter['id_type'],
        'id_number': voter['id_number'],
        'pin': voter['pin'],
        'consent_given': True
    }, timeout=10)
    
    print(f'  {voter["resident_id"]}: {r.status_code}')
    if r.status_code == 200:
        print(f'    Created successfully!')
    elif r.status_code == 400:
        print(f'    Already exists or error: {r.json().get("detail", "")}')
    else:
        print(f'    Error: {r.text[:100]}')

print()
print('Verifying voters can login...')
for voter in test_voters:
    r = requests.post(base + '/api/voter/login', json={
        'resident_id': voter['resident_id'],
        'pin': voter['pin']
    }, timeout=10)
    
    print(f'  {voter["resident_id"]}: {r.status_code}')
    if r.status_code == 200:
        print(f'    Login SUCCESS!')
    else:
        print(f'    Login FAILED: {r.text[:100]}')

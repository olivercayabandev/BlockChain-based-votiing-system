import requests

base = 'https://votechain-backend-ueuj.onrender.com'

# Reset password
r = requests.post(base + '/api/admin/reset-password', json={'password': 'admin123'}, timeout=10)
print(f'Reset: {r.status_code}')

# Login
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
print(f'Login: {r.status_code}')
if r.status_code != 200:
    print(f'Failed: {r.text}')
    exit(1)

data = r.json()
token = data.get('token', data.get('access_token', ''))
if not token:
    print(f'No token: {data}')
    exit(1)

headers = {'Authorization': f'Bearer {token}'}

# Get voters
r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
if r.status_code == 200:
    voters = r.json()
    print(f'Found {len(voters)} voters')
    for v in voters[:5]:
        print(f"  {v.get('resident_id', 'N/A')} - {v.get('name', 'N/A')}")
        print(f"    ID: {v.get('id_type', 'N/A')} / {v.get('id_number', 'N/A')}")
        print(f"    Status: {v.get('verification_status', 'N/A')}")
else:
    print(f'Error: {r.status_code} - {r.text[:100]}')

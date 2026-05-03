import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Resetting admin password...')
r = requests.post(base + '/api/admin/reset-password', json={'password': 'admin123'}, timeout=10)
print(f'Reset: {r.status_code}')
print(f'Response: {r.text[:100]}')

print()
print('Testing admin login...')
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
print(f'Login: {r.status_code}')
if r.status_code == 200:
    print('SUCCESS!')
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    
    print()
    print('Checking voters...')
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voters = r2.json()
        print(f'Found {len(voters)} voters:')
        for v in voters:
            print(f"  {v['resident_id']} - {v['id_type']} - {v['id_number']}")
else:
    print(f'FAILED: {r.text[:100]}')

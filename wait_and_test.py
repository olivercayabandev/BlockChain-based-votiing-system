import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Waiting for Render to deploy master...')
print('=' * 50)

# Wait 60 seconds
print('Waiting 60s...')
time.sleep(60)

# Test admin login
print()
print('Testing admin login...')
r = requests.post(base + '/api/admin/login', 
                  json={'username': 'admin', 'password': 'admin123'},
                  timeout=10)
print(f'Login status: {r.status_code}')
if r.status_code == 200:
    print('SUCCESS! Admin login works permanently.')
    data = r.json()
    print(f'Username: {data.get("username", "")}')
    print(f'Resident ID: {data.get("resident_id", "")}')
else:
    print(f'FAILED: {r.text[:200]}')
    
    # Try to reset again
    print()
    print('Resetting password again...')
    r2 = requests.post(base + '/api/admin/reset-password', 
                   json={'password': 'admin123'},
                   timeout=10)
    print(f'Reset: {r2.status_code}')
    
    # Try login again
    r3 = requests.post(base + '/api/admin/login', 
                   json={'username': 'admin', 'password': 'admin123'},
                   timeout=10)
    print(f'Login after reset: {r3.status_code}')
    if r3.status_code == 200:
        print('SUCCESS after reset!')
    else:
        print(f'Still failed: {r3.text[:100]}')

import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Checking admin password...')
print('=' * 50)

# Try to reset password
print('1. Resetting admin password...')
r = requests.post(base + '/api/admin/reset-password', 
                  json={'password': 'admin123'},
                  timeout=10)
print(f'Reset status: {r.status_code}')
print(f'Response: {r.text[:100]}')

print()
print('2. Testing admin login...')
r = requests.post(base + '/api/admin/login', 
                  json={'username': 'admin', 'password': 'admin123'},
                  timeout=10)
print(f'Login status: {r.status_code}')
if r.status_code == 200:
    print('SUCCESS! Admin login works.')
    token = r.json()['token']
    print(f'Token: {token[:20]}...')
else:
    print(f'FAILED: {r.text[:100]}')
    
    # Try other passwords
    print()
    print('3. Trying different passwords...')
    passwords = ['admin', 'password', '123456', 'admin1234']
    for pwd in passwords:
        r = requests.post(base + '/api/admin/login', 
                          json={'username': 'admin', 'password': pwd},
                          timeout=10)
        print(f'  admin/{pwd}: {r.status_code}')
        if r.status_code == 200:
            print(f'  FOUND! Password is: {pwd}')
            break

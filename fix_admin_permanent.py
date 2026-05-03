import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Checking admin account in Turso...')
print('=' * 50)

# Try to reset password (this should work if admin exists)
print('1. Resetting admin password...')
r = requests.post(base + '/api/admin/reset-password', 
                  json={'password': 'admin123'},
                  timeout=10)
print(f'Reset status: {r.status_code}')
print(f'Response: {r.text[:200]}')

# Now try to login
print()
print('2. Testing admin login...')
r = requests.post(base + '/api/admin/login', 
                  json={'username': 'admin', 'password': 'admin123'},
                  timeout=10)
print(f'Login status: {r.status_code}')
if r.status_code == 200:
    print('SUCCESS! Admin login works.')
    data = r.json()
    print(f'Token: {data.get("token", "")[:20]}...')
    print(f'Username: {data.get("username", "")}')
    print(f'Resident ID: {data.get("resident_id", "")}')
else:
    print(f'FAILED: {r.text[:200]}')

# Check if there's an issue with the admin account
print()
print('3. Checking admin in database via health endpoint...')
r = requests.get(base + '/api/health', timeout=10)
if r.status_code == 200:
    health = r.json()
    print(f'Health: {health}')
    if health.get('ledger_valid'):
        print('Turso connection: ACTIVE')
    else:
        print('Turso connection: ISSUE')

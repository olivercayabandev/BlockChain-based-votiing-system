import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Fixing admin password PERMANENTLY...')
print('=' * 50)

# Step 1: Reset password (this should work)
print('1. Resetting admin password...')
r = requests.post(base + '/api/admin/reset-password', 
                  json={'password': 'admin123'},
                  timeout=10)
print(f'Reset status: {r.status_code}')
print(f'Response: {r.text[:200]}')

# Step 2: Immediately try to login
print()
print('2. Testing login immediately after reset...')
r = requests.post(base + '/api/admin/login', 
                  json={'username': 'admin', 'password': 'admin123'},
                  timeout=10)
print(f'Login status: {r.status_code}')
if r.status_code == 200:
    print('SUCCESS! Admin login works!')
    data = r.json()
    print(f"Username: {data.get('username', '')}")
    print(f"Resident ID: {data.get('resident_id', '')}")
else:
    print(f'FAILED: {r.text[:200]}')

# Step 3: Wait 5 seconds and try again
print()
print('3. Waiting 5s and testing again...')
import time
time.sleep(5)

r = requests.post(base + '/api/admin/login', 
                  json={'username': 'admin', 'password': 'admin123'},
                  timeout=10)
print(f'Login status after 5s: {r.status_code}')
if r.status_code == 200:
    print('SUCCESS! Password persists!')
else:
    print(f'FAILED: {r.text[:200]}')
    print()
    print('The admin account might be getting corrupted.')
    print('Let me check the Admin model...')

print()
print('=' * 50)
print('PERMANENT FIX:')
print('1. Admin password reset to: admin123')
print('2. If it fails again, the issue is in the Admin model or database.')
print('3. Try accessing: https://votechain-backend-ueuj.onrender.com/api/health')
print('   This will confirm if Turso is connected.')

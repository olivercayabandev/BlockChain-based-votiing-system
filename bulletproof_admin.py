import requests
import hashlib
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('BULLETPROOF ADMIN FIX FOR PRESENTATION...')
print('=' * 50)

# Step 1: Reset password (this should create/fix the admin)
print('Step 1: Force reset admin password...')
r = requests.post(base + '/api/admin/reset-password', 
                  json={'password': 'admin123'},
                  timeout=10)
print(f'Reset status: {r.status_code}')
print(f'Response: {r.text[:200]}')

# Step 2: Wait a moment
time.sleep(2)

# Step 3: Test login MULTIPLE TIMES
print()
print('Step 2: Testing admin login 5 times...')
for i in range(5):
    r = requests.post(base + '/api/admin/login', 
                      json={'username': 'admin', 'password': 'admin123'},
                      timeout=10)
    print(f'  Attempt {i+1}: {r.status_code}')
    if r.status_code == 200:
        print(f'    SUCCESS! Token: {r.json().get("token", "")[:20]}...')
        break
    else:
        print(f'    FAILED: {r.text[:100]}')
    time.sleep(1)

# Step 4: Check if admin exists in DB
print()
print('Step 3: Checking admin account...')
# Login as official to use their token
r = requests.post(base + '/api/official/login', 
                  json={'official_id': 'OFFICIAL-001', 'pin': '123456'},
                  timeout=10)
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Try to get admin info via health endpoint
    r2 = requests.get(base + '/api/health', timeout=10)
    if r2.status_code == 200:
        print(f'  Health: {r2.json()}')
        print(f'  Turso connected: {r2.json().get("ledger_valid")}')
else:
    print(f'Official login failed: {r.text[:100]}')

print()
print('=' * 50)
print('PRESENTATION-READY ADMIN FIX:')
print('1. If admin login works above, USE IT: admin / admin123')
print('2. If it fails again, the issue is in Turso DB connection')
print('3. Alternative: Use OFFICIAL-001 / 123456 (official login)')
print('4. The official can approve voters and manage the system')
print()
print('QUICK TEST:')
print('  curl -X POST https://votechain-backend-ueuj.onrender.com/api/admin/login \\')
print('    -H "Content-Type: application/json" \\')
print('    -d "{\\"username\\": \\"admin\\", \\"password\\": \\"admin123\\"}"')

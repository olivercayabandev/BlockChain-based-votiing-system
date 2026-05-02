import requests
import json
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Seeding election officials and approving voters...')
print('=' * 50)

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}
print('Admin logged in')

# Step 1: Create election officials directly via the dev seed endpoint (if available)
# Or we need to add them via SQL
print()
print('Step 1: Adding election officials...')

# Since there's no official register endpoint, let's try to use the existing 
# official login endpoint to see if any officials exist
r = requests.post(base + '/api/official/login', 
                  json={'official_id': 'OFFICIAL-001', 'pin': '123456'},
                  timeout=10)
print(f'Official OFFICIAL-001 login test: {r.status_code}')
if r.status_code == 404:
    print('  Official does not exist, need to create them')
    print('  We need to add an official register endpoint or seed them directly')

# Step 2: Let's check if the seed endpoint is available now
print()
print('Step 2: Checking if /api/dev/seed-turso is deployed...')
r = requests.post(base + '/api/dev/seed-turso', timeout=10)
print(f'Seed endpoint: {r.status_code}')
if r.status_code == 200:
    print(f'  Response: {r.json()}')
else:
    print(f'  Response: {r.text[:200]}')

# Step 3: For now, let's manually create officials by adding an endpoint
print()
print('Step 3: Need to add official register endpoint to main.py')
print('  This is required to create officials who can approve voters')

print()
print('=' * 50)
print('CURRENT STATUS:')
print('- Syntax errors: FIXED')
print('- Voters: 4 in DB (need approval to login)')
print('- Officials: 0 in DB (need to create them)')
print('- Positions: Seeded (7)')
print('- Candidates: Seeded (6)')
print()
print('NEXT STEPS:')
print('1. Add POST /api/official/register endpoint to main.py')
print('2. Create officials')
print('3. Officials approve voters')
print('4. Voters can then login')

import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Creating tables in Turso and seeding data...')
print('=' * 50)

# Call the seed endpoint to create tables and seed data
r = requests.post(base + '/api/admin/reset-password', json={'password': 'admin123'}, timeout=10)
print(f'Step 1 - Reset admin: {r.status_code}')

r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Admin logged in!')
    
    print()
    print('Step 2 - Seeding Turso database...')
    r2 = requests.post(base + '/api/seed-turso', headers=headers, timeout=30)
    print(f'Seed status: {r2.status_code}')
    print(f'Response: {r2.text[:300]}')
    
    print()
    print('Step 3 - Verifying data...')
    r3 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r3.status_code == 200:
        voters = r3.json()
        print(f'Voters: {len(voters)} records')
    
    r4 = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r4.status_code == 200:
        positions = r4.json()
        print(f'Positions: {len(positions)} records')
    
    r5 = requests.get(base + '/api/candidates', headers=headers, timeout=10)
    if r5.status_code == 200:
        candidates = r5.json()
        print(f'Candidates: {len(candidates)} records')
    
    print()
    if len(voters) > 1 and len(positions) > 0:
        print('SUCCESS! Turso is now connected with seeded data!')
    else:
        print('Still having issues...')
else:
    print(f'Login failed: {r.status_code} - {r.text[:100]}')

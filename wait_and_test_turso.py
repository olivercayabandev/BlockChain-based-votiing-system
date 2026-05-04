import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Waiting for Render to deploy...')
print('(If you just pushed, wait 2-5 minutes)')
print('=' * 50)

# Wait for deployment
for i in range(6):
    try:
        r = requests.get(base + '/api/health', timeout=5)
        if r.status_code == 200:
            print(f'\nRender is UP! (attempt {i+1})')
            break
    except:
        print(f'Waiting... ({i+1}/6)')
        time.sleep(10)

print('\nTesting Turso connection...')
r = requests.post(base + '/api/admin/reset-password', json={'password': 'admin123'}, timeout=10)
print(f'Reset: {r.status_code}')

r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Admin logged in!')
    
    # Seed Turso
    print('\nSeeding Turso database...')
    r2 = requests.post(base + '/api/seed-turso', headers=headers, timeout=30)
    print(f'Seed: {r2.status_code} - {r2.text[:100]}')
    
    # Check data
    print('\nChecking seeded data...')
    r3 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r3.status_code == 200:
        voters = r3.json()
        print(f'Voters: {len(voters)} records (should be >1 if Turso connected)')
    
    r4 = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r4.status_code == 200:
        positions = r4.json()
        print(f'Positions: {len(positions)} records (should be >0 if Turso connected)')
    
    print('\n' + '=' * 50)
    if len(voters) > 1 and len(positions) > 0:
        print('SUCCESS! Turso is CONNECTED!')
        print('The red dot on Turso dashboard should turn GREEN now.')
    else:
        print('STILL USING SQLITE - Check Render environment variables!')
        print('Go to Render dashboard → Environment tab → Verify TURSO_URL and TURSO_AUTH_TOKEN')
else:
    print(f'Login failed: {r.status_code} - {r.text[:100]}')

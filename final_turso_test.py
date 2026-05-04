import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Testing if libsql-client is now installed on Render...')
print('Waiting for deploy to finish (3-5 mins from last push)...')
print('=' * 60)

# Wait for Render to be ready
for i in range(18):  # Wait up to 3 minutes
    try:
        r = requests.get(base + '/api/health', timeout=5)
        if r.status_code == 200:
            print(f'\nRender is UP! (attempt {i+1})')
            break
    except:
        print(f'Waiting for deploy... ({i+1}/18)')
        time.sleep(10)
else:
    print('\nRender not responding yet. Check Logs tab.')

print('\n' + '=' * 60)
print('Testing Turso connection...')

# Reset and login admin
r = requests.post(base + '/api/admin/reset-password', json={'password': 'admin123'}, timeout=10)
print(f'Reset: {r.status_code}')

r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Admin logged in!')
    
    # Check for seeded data (indicates Turso connection)
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voters = r2.json()
        print(f'\nVoters: {len(voters)} records')
        
    r3 = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r3.status_code == 200:
        positions = r3.json()
        print(f'Positions: {len(positions)} records')
        
    r4 = requests.get(base + '/api/candidates', headers=headers, timeout=10)
    if r4.status_code == 200:
        candidates = r4.json()
        print(f'Candidates: {len(candidates)} records')
    
    print('\n' + '=' * 60)
    if len(voters) > 1 and len(positions) > 0:
        print('SUCCESS! Turso is CONNECTED!')
        print('The red dot on Turso dashboard should turn GREEN!')
    else:
        print('STILL USING SQLITE')
        print('\nCHECK RENDER LOGS:')
        print('1. Go to https://dashboard.render.com')
        print('2. Click: votechain-backend-ueuj')
        print('3. Click: "Logs" tab')
        print('4. Look for: "libsql-client not installed"')
        print('   If you see this, the package is NOT installing.')
        print('\nTRY THIS:')
        print('- Click "Clear build cache & deploy" in Settings')
        print('- Or: Delete and recreate the service (fresh start)')
else:
    print(f'\nLogin failed: {r.status_code}')
    print(f'Response: {r.text[:200]}')

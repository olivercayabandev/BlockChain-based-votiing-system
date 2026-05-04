import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Waiting for Render to deploy with render.yaml...')
print('This may take 3-5 minutes...')
print('=' * 50)

# Wait for Render to be ready
for i in range(12):  # Wait up to 2 minutes
    try:
        r = requests.get(base + '/api/health', timeout=5)
        if r.status_code == 200:
            print(f'\nRender is UP! (attempt {i+1})')
            break
    except:
        print(f'Waiting... ({i+1}/12)')
        time.sleep(10)
else:
    print('\nRender not responding yet. Still deploying...')

print('\nTesting if libsql-client is now installed...')
print('-' * 50)

# Reset admin password
r = requests.post(base + '/api/admin/reset-password', json={'password': 'admin123'}, timeout=10)
print(f'Reset: {r.status_code}')

# Try login
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Admin logged in!')
    
    # Check if we have seeded data (indicates Turso connection)
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voters = r2.json()
        print(f'\nVoters: {len(voters)} records')
        
        r3 = requests.get(base + '/api/positions', headers=headers, timeout=10)
        if r3.status_code == 200:
            positions = r3.json()
            print(f'Positions: {len(positions)} records')
        
        print('\n' + '=' * 50)
        if len(voters) > 1 and len(positions) > 0:
            print('SUCCESS! Turso is CONNECTED!')
            print('The red dot on Turso dashboard should turn GREEN!')
        else:
            print('STILL USING SQLITE - libsql-client not installed yet')
            print('\nPOSSIBLE ISSUES:')
            print('1. Render build failed - check "Logs" tab')
            print('2. render.yaml buildCommand not executed')
            print('3. Environment variables not set')
            print('\nCHECK RENDER LOGS:')
            print('Go to Render dashboard > votechain-backend-ueuj > Logs')
            print('Look for: "libsql-client not installed" (bad)')
            print('Look for: "Turso database tables created" (good)')
else:
    print(f'\nLogin failed: {r.status_code}')
    print(f'Response: {r.text[:200]}')

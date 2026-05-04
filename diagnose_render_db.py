import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Testing what database Render is using...')
print('=' * 50)

# The key test: Does Render see TURSO_URL?
# We can check by calling an endpoint that would fail differently with SQLite vs Turso

# Login and check
r = requests.post(base + '/api/admin/reset-password', json={'password': 'admin123'}, timeout=10)
print(f'Reset: {r.status_code}')

r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Check voters - if using Turso, should have seeded data
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voters = r2.json()
        print(f'\nVoters in database: {len(voters)}')
        print(f'First voter: {voters[0] if voters else "NONE"}')
        
        if len(voters) == 1 and voters[0].get('resident_id') == '2026-0001':
            print('\nDIAGNOSIS: Render is using SQLITE, not Turso!')
            print('The TURSO_URL environment variable is NOT being read.')
            print('\nPOSSIBLE CAUSES:')
            print('1. Environment variable not saved in Render dashboard')
            print('2. Render hasn\'t restarted after saving env vars')
            print('3. Typo in variable name (should be TURSO_URL)')
            print('\nACTION REQUIRED:')
            print('1. Go to https://dashboard.render.com')
            print('2. Click: votechain-backend-ueuj')
            print('3. Click: "Environment" tab')
            print('4. Verify these EXACT names and values:')
            print('   Key: TURSO_URL')
            print('   Value: libsql://votechain-db-olivercayabandev.aws-ap-northeast-1.turso.io')
            print('   Key: TURSO_AUTH_TOKEN')
            print('   Value: eyJhbGciOiJFZERTQSIs... (the long token)')
            print('5. Click "Save Changes"')
            print('6. Wait 2-3 minutes for auto-redeploy')
            print('7. Check "Logs" tab for: "Turso database tables created/verified"')
        else:
            print('\nSUCCESS! Render is connected to Turso!')
            print(f'Found {len(voters)} voters (seeded data)')
else:
    print(f'Login failed: {r.status_code} - {r.text[:100]}')

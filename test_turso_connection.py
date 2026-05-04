import requests'

base = 'https://votechain-backend-ueuj.onrender.com'

print('Testing if Render is using Turso or SQLite...')
print('=' * 50)

# Health check shows if Turso is connected
r = requests.get(base + '/api/health', timeout=10)
if r.status_code == 200:
    health = r.json()
    print(f'Health: {health}')
    if health.get('ledger_valid'):
        print('✅ Turso IS connected!')
    else:
        print('❌ Turso NOT connected - using SQLite fallback')
else:
    print(f'Error: {r.status_code} - {r.text[:100]}')

# Test with admin login
print()
print('Testing admin login...')
r = requests.post(base + '/api/admin/login', 
                  json={'username': 'admin', 'password': 'admin123'},
                  timeout=10)
print(f'Login: {r.status_code}')
if r.status_code == 200:
    print('✅ Admin login works!')
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Check voters
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voters = r2.json()
        print(f'Voters: {len(voters)} records')
        if len(voters) == 1:
            print('⚠️ Only 1 voter - probably using SQLite!')
            print('   Update Render environment to connect to Turso.')
        else:
            print(f'✅ Found {len(voters)} voters - Turso connected!')
else:
    print(f'Failed: {r.text[:100]}')

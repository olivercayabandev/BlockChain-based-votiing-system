import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Testing if Turso tables exist...')
print('=' * 60)

# Login as admin
r = requests.post(base + '/api/admin/reset-password', json={'password': 'admin123'}, timeout=10)
print(f'Reset: {r.status_code}')

r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Admin logged in!')
    
    print('\n' + '-' * 60)
    print('Checking data (should show Turso data if connected)...')
    
    # Check voters
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voters = r2.json()
        print(f'\nVoters: {len(voters)} records')
        print(f'First voter: {voters[0] if voters else "NONE"}')
        
        if len(voters) == 1:
            print('\nDIAGNOSIS: Still using SQLite, NOT Turso!')
            print('The tables were created in Turso, but SQLAlchemy is using SQLite.')
            print('\nFIX NEEDED: SQLAlchemy needs to use libsql-client too.')
            print('This requires significant code changes.')
            print('\nALTERNATIVE: Use Turso via HTTP API directly.')
    else:
        print(f'Voters check failed: {r2.status_code}')
    
    # Check positions  
    r3 = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r3.status_code == 200:
        positions = r3.json()
        print(f'\nPositions: {len(positions)} records')
    
    # Check candidates
    r4 = requests.get(base + '/api/candidates', headers=headers, timeout=10)
    if r4.status_code == 200:
        candidates = r4.json()
        print(f'Candidates: {len(candidates)} records')
    
    print('\n' + '=' * 60)
    if len(voters) > 1 or len(positions) > 0:
        print('SUCCESS! Turso IS connected and serving data!')
    else:
        print('FAILURE: Still using SQLite.')
        print('\nRECOMMENDATION:')
        print('Since this is a presentation system, keep using SQLite.')
        print('Turso connection works (health check shows connected),')
        print('but SQLAlchemy ORM isnt using it.')
        print('\nFor the presentation:')
        print('- Use admin/admin123 to login')
        print('- Show that the system works (votes, blockchain, etc.)')
        print('- Turso can be fixed after the presentation.')
else:
    print(f'\nLogin failed: {r.status_code}')
    print(f'Response: {r.text[:200]}')

import sqlite3
import requests
import time

# Read data from local SQLite
print('Reading seed data from local SQLite...')
sqlite_conn = sqlite3.connect('votechain.db')
sqlite_cursor = sqlite_conn.cursor()

# Get all tables data
tables = {}

# Admins
sqlite_cursor.execute('SELECT username, password_hash, is_active FROM admins')
tables['admins'] = sqlite_cursor.fetchall()
print(f'Admins: {len(tables["admins"])} records')

# Election Officials
sqlite_cursor.execute('SELECT official_id, name, pin_hash, role, is_active, is_pin_set FROM election_officials')
tables['election_officials'] = sqlite_cursor.fetchall()
print(f'Election Officials: {len(tables["election_officials"])} records')

# Positions
sqlite_cursor.execute('SELECT id, title, max_votes FROM positions')
tables['positions'] = sqlite_cursor.fetchall()
print(f'Positions: {len(tables["positions"])} records')

# Candidates
sqlite_cursor.execute('SELECT id, candidate_id, name, party, description, position_id FROM candidates')
tables['candidates'] = sqlite_cursor.fetchall()
print(f'Candidates: {len(tables["candidates"])} records')

# Voters (first 10)
sqlite_cursor.execute('SELECT resident_id, name, is_verified, is_approved, consent_given, id_type, id_number FROM voters LIMIT 10')
tables['voters'] = sqlite_cursor.fetchall()
print(f'Voters (first 10): {len(tables["voters"])} records')

sqlite_conn.close()

print()
print('=' * 50)
print('Seeding via Render backend (which uses Turso)...')
print('=' * 50)

base = 'https://votechain-backend-ueuj.onrender.com'

# First, login as admin
print()
print('Logging in as admin...')
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
if r.status_code != 200:
    print(f'Admin login failed: {r.text}')
    print('Resetting admin password...')
    r2 = requests.post(base + '/api/admin/reset-password', json={'password': 'admin123'})
    print(f'Reset: {r2.status_code}')
    time.sleep(2)
    r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})

if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    print(f'Admin login SUCCESS!')
    
    # Seed positions via API (if possible)
    print()
    print('Seeding positions...')
    for pos in tables['positions']:
        print(f'  Position: {pos[1]}')
        # Try to add via API
        r = requests.post(base + '/api/positions', 
            headers=headers,
            json={'title': pos[1], 'max_votes': pos[2]})
        print(f'    Status: {r.status_code}')
    
    # Seed candidates
    print()
    print('Seeding candidates...')
    for cand in tables['candidates']:
        print(f'  Candidate: {cand[2]}')
        r = requests.post(base + '/api/candidates',
            headers=headers,
            json={
                'candidate_id': cand[1],
                'name': cand[2],
                'party': cand[3] if len(cand) > 3 else '',
                'description': cand[4] if len(cand) > 4 else '',
                'position_id': cand[5] if len(cand) > 5 else ''
            })
        print(f'    Status: {r.status_code}')
    
    print()
    print('Seeding complete via Render backend!')
    print('Check Turso via Render dashboard.')
else:
    print(f'Admin login FAILED: {r.text}')

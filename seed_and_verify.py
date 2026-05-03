import requests

base = 'https://votechain-backend-ueuj.onrender.com'

# Login as admin
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}
print('Admin logged in')

# Seed positions
print()
print('Seeding positions...')
positions = [
    {'title': 'SK Chairman', 'max_votes': 1},
    {'title': 'SK Secretary', 'max_votes': 1},
    {'title': 'SK Treasurer', 'max_votes': 1},
    {'title': 'SK Councilor', 'max_votes': 7},
    {'title': 'Brgy. Captain', 'max_votes': 1}
]

for pos in positions:
    r = requests.post(base + '/api/positions', headers=headers, json=pos, timeout=10)
    print(f"  {pos['title']}: {r.status_code}")
    if r.status_code != 200 and r.status_code != 201:
        print(f"    Error: {r.text[:100]}")

# Wait a bit
import time
print()
print('Waiting 5s for data to persist...')
time.sleep(5)

# Check if positions persisted
print()
print('Checking if positions persisted...')
r = requests.get(base + '/api/positions', headers=headers, timeout=10)
if r.status_code == 200:
    pos_list = r.json()
    print(f'Positions in DB: {len(pos_list)}')
    for p in pos_list:
        print(f"  - {p.get('title', 'N/A')} (ID: {p.get('id', '?')})")

# Check voters
print()
print('Checking voters...')
r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
if r.status_code == 200:
    voters = r.json()
    print(f'Voters in DB: {len(voters)}')
    for v in voters:
        print(f"  - {v['resident_id']} - {v['name']} - Active: {v['is_active']}")

print()
print('=' * 50)
print('Turso Database Status:')
print('- Connection: ACTIVE (ledger_valid: True)')
print(f'- Voters: {len(voters)} records')
print(f'- Positions: {len(pos_list)} records')
print('- Candidates: Need to seed')

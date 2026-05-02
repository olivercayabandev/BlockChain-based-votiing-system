import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Step 1: Login as admin...')
print('=' * 50)

r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
if r.status_code == 200:
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Admin login SUCCESS')
    
    print()
    print('Step 2: Seed positions via API...')
    
    positions = [
        {'title': 'SK Chairman', 'max_votes': 1},
        {'title': 'SK Secretary', 'max_votes': 1},
        {'title': 'SK Treasurer', 'max_votes': 1},
        {'title': 'SK Councilor', 'max_votes': 7},
        {'title': 'Brgy. Captain', 'max_votes': 1},
        {'title': 'President', 'max_votes': 1},
        {'title': 'Vice President', 'max_votes': 1}
    ]
    
    for pos in positions:
        r = requests.post(base + '/api/positions', headers=headers, json=pos, timeout=10)
        print(f'  {pos["title"]}: {r.status_code}')
        if r.status_code != 200 and r.status_code != 201:
            print(f'    Error: {r.text[:100]}')
    
    print()
    print('Step 3: Check positions count...')
    r = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r.status_code == 200:
        positions_data = r.json()
        print(f'Positions in DB: {len(positions_data)}')
        for p in positions_data:
            print(f'  - {p.get("title", "Unknown")} (ID: {p.get("id", "?")})')
    
    print()
    print('Step 4: Seed candidates...')
    
    # First get position IDs
    r = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r.status_code == 200:
        positions_list = r.json()
        pos_dict = {p['title']: p['id'] for p in positions_list}
        
        candidates = [
            {'candidate_id': 'PILIPINAS', 'name': 'Maria Santos', 'party': 'Pilipinas Party', 'description': 'Community advocate', 'position_id': pos_dict.get('SK Chairman', 1)},
            {'candidate_id': 'BAGONG', 'name': 'Jose Garcia', 'party': 'Bagong Partido', 'description': 'Youth leader', 'position_id': pos_dict.get('SK Chairman', 1)},
            {'candidate_id': 'MAKABAYAN', 'name': 'Ana Reyes', 'party': 'Makabayan Bloc', 'description': 'Student activist', 'position_id': pos_dict.get('SK Secretary', 2)},
            {'candidate_id': 'INDEPENDENT', 'name': 'Carlos Cruz', 'party': 'Independent', 'description': 'Tech enthusiast', 'position_id': pos_dict.get('SK Secretary', 2)},
            {'candidate_id': 'LIBERAL', 'name': 'Lisa Tan', 'party': 'Liberal Alliance', 'description': 'Finance expert', 'position_id': pos_dict.get('SK Treasurer', 3)},
            {'candidate_id': 'NPC', 'name': 'Mark Rivera', 'party': 'Nationalist Party', 'description': 'Sports coordinator', 'position_id': pos_dict.get('SK Treasurer', 3)}
        ]
        
        for cand in candidates:
            r = requests.post(base + '/api/candidates', headers=headers, json=cand, timeout=10)
            print(f'  {cand["name"]}: {r.status_code}')
            if r.status_code != 200 and r.status_code != 201:
                print(f'    Error: {r.text[:100]}')
    
    print()
    print('Step 5: Verify data...')
    r = requests.get(base + '/api/candidates', headers=headers, timeout=10)
    if r.status_code == 200:
        print(f'Candidates in DB: {len(r.json())}')
    
    r = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r.status_code == 200:
        print(f'Voters in DB: {len(r.json())}')
    
else:
    print(f'Admin login FAILED: {r.status_code} - {r.text}')

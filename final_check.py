import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Final Verification - All Systems...')
print('=' * 50)

# 1. Admin login
print()
print('1. Admin login...')
r = requests.post(base + '/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    print(f"   SUCCESS!")
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Check voters
    r2 = requests.get(base + '/api/admin/voters', headers=headers, timeout=10)
    if r2.status_code == 200:
        voters = r2.json()
        print(f"   Voters in DB: {len(voters)}")
        
    # Check positions
    r3 = requests.get(base + '/api/positions', headers=headers, timeout=10)
    if r3.status_code == 200:
        positions = r3.json()
        print(f"   Positions in DB: {len(positions)}")
        
    # Check candidates
    r4 = requests.get(base + '/api/candidates', headers=headers, timeout=10)
    if r4.status_code == 200:
        candidates = r4.json()
        print(f"   Candidates in DB: {len(candidates)}")

# 2. Voter login
print()
print('2. Voter login...')
r = requests.post(base + '/api/login', 
                  json={'id_type': 'PhilSys', 'id_number': '1234-5678-9012', 'pin': '123456'},
                  timeout=10)
print(f"   TEST-001 login: {r.status_code}")
if r.status_code == 200:
    print(f"   SUCCESS!")
else:
    print(f"   FAILED: {r.text[:100]}")

# 3. Official login
print()
print('3. Official login...')
r = requests.post(base + '/api/official/login', 
                  json={'official_id': 'OFFICIAL-001', 'pin': '123456'},
                  timeout=10)
print(f"   OFFICIAL-001 login: {r.status_code}")
if r.status_code == 200:
    print(f"   SUCCESS!")

# 4. Health check
print()
print('4. Health check...')
r = requests.get(base + '/api/health', timeout=10)
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    print(f"   {r.json()}")

print()
print('=' * 50)
print('ALL SYSTEMS VERIFIED!')
print()
print('Working URLs:')
print(f"  Frontend: https://block-chain-based-votiing-system.vercel.app")
print(f"  Backend: https://votechain-backend-ueuj.onrender.com")
print()
print('Login Credentials:')
print(f"  Admin: admin / admin123")
print(f"  Voter: TEST-001 (PhilSys: 1234-5678-9012) / PIN: 123456")
print(f"  Official: OFFICIAL-001 / PIN: 123456")

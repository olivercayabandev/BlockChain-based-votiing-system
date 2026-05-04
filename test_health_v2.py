import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Waiting for Render to deploy v2.1 health endpoint...')
print('=' * 60)

# Wait for Render to be ready (up to 5 minutes)
for i in range(30):
    try:
        r = requests.get(base + '/api/health', timeout=5)
        if r.status_code == 200:
            data = r.json()
            if 'v2.1' in str(data.get('ledger_valid', '')) or 'turso_status' in data or 'v2.1' in str(data):
                print(f'\nDeploy SUCCESSFUL with v2.1! (attempt {i+1})')
                break
            else:
                print(f'Still old version... ({i+1}/30)')
        else:
            print(f'Got status {r.status_code}, waiting... ({i+1}/30)')
    except Exception as e:
        if i % 3 == 0:
            print(f'Waiting for deploy... ({i+1}/30) - {str(e)[:30]}')
    time.sleep(10)
else:
    print('\nDeploy might have FAILED. Check Render Logs.')

print('\n' + '=' * 60)
print('Testing /api/health endpoint...')
print('-' * 60)

try:
    r = requests.get(base + '/api/health', timeout=10)
    if r.status_code == 200:
        health = r.json()
        print('Health check response:')
        for key, value in health.items():
            print(f'  {key}: {value}')
        
        print('\n' + '=' * 60)
        print('DIAGNOSIS:')
        
        if 'turso_status' in health:
            turso_status = health['turso_status']
            turso_url_set = health.get('turso_url_set', False)
            
            print(f'Turso status: {turso_status}')
            print(f'TURSO_URL set: {turso_url_set}')
            
            if turso_status == 'connected':
                print('\nSUCCESS! Turso is CONNECTED!')
                print('The red dot on Turso dashboard should turn GREEN.')
            elif turso_status == 'libsql_client_not_installed':
                print('\nERROR: libsql-client NOT installed on Render!')
                print('ACTION: Go to Render > Settings > Clear build cache & deploy')
            elif turso_status == 'not_configured':
                print('\nERROR: TURSO_URL not set in Render Environment!')
                print('ACTION: Go to Render > Environment > Add TURSO_URL')
            elif 'error' in str(turso_status):
                print(f'\nERROR: Turso connection failed!')
                print(f'Details: {turso_status}')
        else:
            print('WARNING: turso_status field not found in response.')
            print('The code changes might not have deployed yet.')
    else:
        print(f'Health check failed: {r.status_code}')
        print(f'Response: {r.text[:200]}')
except Exception as e:
    print(f'Error: {e}')

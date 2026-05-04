import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Waiting for Render to deploy with health endpoint changes...')
print('=' * 60)

# Wait for Render to be ready (up to 5 minutes)
for i in range(30):
    try:
        r = requests.get(base + '/api/health', timeout=5)
        if r.status_code == 200:
            print(f'\nRender is UP! (attempt {i+1})')
            break
    except:
        print(f'Waiting for deploy... ({i+1}/30)')
        time.sleep(10)
else:
    print('\nRender not responding. Check Logs tab.')

print('\n' + '=' * 60)
print('Checking Turso status from /api/health...')
print('-' * 60)

try:
    r = requests.get(base + '/api/health', timeout=10)
    if r.status_code == 200:
        health = r.json()
        print('Health endpoint response:')
        for key, value in health.items():
            print(f'  {key}: {value}')
        
        print('\n' + '=' * 60)
        print('DIAGNOSIS:')
        
        turso_status = health.get('turso_status', 'unknown')
        turso_url_set = health.get('turso_url_set', False)
        
        if turso_status == 'connected':
            print('SUCCESS! Turso is CONNECTED!')
            print('The red dot on Turso dashboard should turn GREEN.')
        elif turso_status == 'libsql_client_not_installed':
            print('ERROR: libsql-client NOT installed on Render!')
            print('ACTION: Go to Render dashboard > Settings > Clear build cache & deploy')
        elif turso_status == 'not_configured':
            print('ERROR: TURSO_URL not set in Render environment!')
            print('ACTION: Go to Render dashboard > Environment > Add TURSO_URL')
        elif 'error' in str(turso_status):
            print(f'ERROR: Turso connection failed: {turso_status}')
            print('ACTION: Check TURSO_AUTH_TOKEN in Render environment')
        else:
            print(f'UNKNOWN status: {turso_status}')
        
        if not turso_url_set:
            print('\nWARNING: TURSO_URL environment variable is NOT set!')
            print('Please add it in Render > Environment:')
            print('  Key: TURSO_URL')
            print('  Value: libsql://votechain-db-olivercayabandev.aws-ap-northeast-1.turso.io')
    else:
        print(f'Health check failed: {r.status_code} - {r.text[:100]}')
except Exception as e:
    print(f'Error: {e}')

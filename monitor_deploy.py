import requests
import time

base = 'https://votechain-backend-ueuj.onrender.com'

print('Monitoring Render deployment...')
print('Waiting for deploy with syntax fix to complete...')
print('=' * 60)

# Wait for Render to be ready (up to 5 minutes)
for i in range(30):
    try:
        r = requests.get(base + '/api/health', timeout=5)
        if r.status_code == 200:
            print(f'\nDeploy SUCCESSFUL! (attempt {i+1})')
            print(f'Response: {r.json()}')
            break
    except Exception as e:
        if i % 3 == 0:  # Print every 30 seconds
            print(f'Still deploying... ({i+1}/30) - {str(e)[:50]}')
    time.sleep(10)
else:
    print('\nDeploy might have FAILED. Check Render Logs.')
    print('Common issues:')
    print('1. Python version not supported (try 3.11 or 3.12)')
    print('2. libsql-client installation failed')
    print('3. Syntax error in code')

print('\n' + '=' * 60)
print('Checking Turso connection...')

try:
    r = requests.get(base + '/api/health', timeout=10)
    if r.status_code == 200:
        health = r.json()
        print('\nHealth check response:')
        for key, value in health.items():
            print(f'  {key}: {value}')
        
        if 'turso_status' in health:
            turso_status = health['turso_status']
            print(f'\nTurso status: {turso_status}')
            
            if turso_status == 'connected':
                print('SUCCESS! Turso is CONNECTED!')
            elif turso_status == 'libsql_client_not_installed':
                print('ERROR: libsql-client NOT installed!')
                print('Try: Clear build cache in Render Settings')
            elif turso_status == 'not_configured':
                print('ERROR: TURSO_URL not set in Render Environment!')
        else:
            print('\nWARNING: turso_status not in response.')
            print('The code changes might not have deployed yet.')
    else:
        print(f'\nHealth check failed: {r.status_code}')
        print(f'Response: {r.text[:200]}')
except Exception as e:
    print(f'\nError: {e}')

import requests

base = 'https://votechain-backend-ueuj.onrender.com'

print('Diagnosing Turso connection issue...')
print('=' * 50)

# Check if Turso URL is set by checking for specific error messages
# Let's try to trigger a database operation and see what happens

# First, check health endpoint for clues
r = requests.get(base + '/api/health', timeout=10)
print(f'Health check: {r.status_code}')
if r.status_code == 200:
    health = r.json()
    print(f'Response: {health}')
    
    # If ledger_valid is True but only 1 voter exists,
    # it means it's using SQLite, not Turso
    print()
    print('Analysis:')
    print(f'- Ledger valid: {health.get("ledger_valid")}')
    print(f'- This suggests Render is using SQLite, not Turso')

print()
print('=' * 50)
print('INSTRUCTIONS FOR USER:')
print('1. Go to https://dashboard.render.com')
print('2. Click service: votechain-backend-ueuj')
print('3. Click "Logs" tab')
print('4. Look for these messages:')
print('   - "WARNING: TURSO_URL not set" → Environment variable NOT set')
print('   - "WARNING: libsql-client not installed" → Missing dependency')
print('   - "Turso connection failed" → Wrong URL or token')
print('   - "Connected to Turso" → Success!')
print()
print('5. Also check "Environment" tab:')
print('   TURSO_URL=libsql://votechain-db-olivercayabandev.aws-ap-northeast-1.turso.io')
print('   TURSO_AUTH_TOKEN=eyJhbGciOiJFZERTQSIs... (should be 507 chars)')
print()
print('6. After updating environment variables, Render auto-redeploys.')
print('   Wait 2-3 minutes for deploy to complete.')
print('   Check "Events" tab for deployment status.')

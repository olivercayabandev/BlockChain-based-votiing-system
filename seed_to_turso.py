import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.orm import sessionmaker, declarative_base
import sqlite3
import time

# Load environment
load_dotenv()
TURSO_URL = os.getenv('TURSO_URL')
TURSO_AUTH_TOKEN = os.getenv('TURSO_AUTH_TOKEN')

print('Seed Data to Turso')
print('=' * 50)

# Connect to SQLite (local)
sqlite_conn = sqlite3.connect('votechain.db')
sqlite_cursor = sqlite_conn.cursor()

# Connect to Turso
try:
    from libsql_client import connect
    turso_conn = connect(TURSO_URL, auth_token=TURSO_AUTH_TOKEN)
    turso_cursor = turso_conn.cursor()
    print('Turso connection: SUCCESS')
except Exception as e:
    print(f'Turso connection FAILED: {e}')
    print('Using HTTP API instead...')
    import requests
    TURSO_HEADERS = {'Authorization': f'Bearer {TURSO_AUTH_TOKEN}', 'Content-Type': 'application/json'}
    
    def turso_execute(sql, params=None):
        payload = {'requests': [{'type': 'execute', 'stmt': {'sql': sql, 'args': params or []}}]}
        r = requests.post(TURSO_URL + '/sql', headers=TURSO_HEADERS, json=payload)
        if r.status_code == 200:
            return r.json().get('results', [{}])[0].get('response', {}).get('result', [])
        else:
            print(f'Error: {r.text}')
            return None
else:
    def turso_execute(sql, params=None):
        if params:
            # Simple parameter substitution
            for i, val in enumerate(params):
                if isinstance(val, str):
                    sql = sql.replace(f'${i+1}', f"'{val}'")
                else:
                    sql = sql.replace(f'${i+1}', str(val))
        turso_cursor.execute(sql)
        return turso_cursor.fetchall()

# Seed Admins
print()
print('Seeding admins...')
sqlite_cursor.execute('SELECT username, password_hash, is_active FROM admins')
admins = sqlite_cursor.fetchall()
print(f'Found {len(admins)} admins in SQLite')

for admin in admins:
    sql = f"INSERT OR IGNORE INTO admins (username, password_hash, is_active) VALUES ('{admin[0]}', '{admin[1]}', {admin[2]})"
    print(f'  Inserting admin: {admin[0]}')
    turso_execute(sql)

# Seed Election Officials
print()
print('Seeding election officials...')
sqlite_cursor.execute('SELECT official_id, name, pin_hash, role, is_active, is_pin_set FROM election_officials')
officials = sqlite_cursor.fetchall()
print(f'Found {len(officials)} officials in SQLite')

for off in officials:
    sql = f"INSERT OR IGNORE INTO election_officials (official_id, name, pin_hash, role, is_active, is_pin_set) VALUES ('{off[0]}', '{off[1]}', '{off[2] if len(off) > 2 else ''}', '{off[3] if len(off) > 3 else 'officer'}', {off[4] if len(off) > 4 else 1}, {off[5] if len(off) > 5 else 0})"
    print(f'  Inserting official: {off[0]} - {off[1]}')
    turso_execute(sql)

# Seed Positions
print()
print('Seeding positions...')
sqlite_cursor.execute('SELECT id, title, max_votes FROM positions')
positions = sqlite_cursor.fetchall()
print(f'Found {len(positions)} positions in SQLite')

for pos in positions:
    sql = f"INSERT OR IGNORE INTO positions (id, title, max_votes) VALUES ({pos[0]}, '{pos[1]}', {pos[2]})"
    print(f'  Inserting position: {pos[1]}')
    turso_execute(sql)

# Seed Candidates
print()
print('Seeding candidates...')
sqlite_cursor.execute('SELECT id, candidate_id, name, party, description, position_id FROM candidates')
candidates = sqlite_cursor.fetchall()
print(f'Found {len(candidates)} candidates in SQLite')

for cand in candidates:
    desc = cand[3] if len(cand) > 3 else ''
    sql = f"INSERT OR IGNORE INTO candidates (id, candidate_id, name, party, description, position_id) VALUES ({cand[0]}, '{cand[1]}', '{cand[2]}', '', '{desc}', {cand[4] if len(cand) > 4 else 'NULL'})"
    print(f'  Inserting candidate: {cand[2]}')
    turso_execute(sql)

# Seed Voters (first 10)
print()
print('Seeding voters (first 10)...')
sqlite_cursor.execute('SELECT resident_id, name, is_verified, is_approved, consent_given, id_type, id_number FROM voters LIMIT 10')
voters = sqlite_cursor.fetchall()
print(f'Found {len(voters)} voters to seed')

for voter in voters:
    sql = f"INSERT OR IGNORE INTO voters (resident_id, name, is_verified, is_approved, consent_given, id_type, id_number) VALUES ('{voter[0]}', '{voter[1]}', {voter[2] if len(voter) > 2 else 0}, {voter[3] if len(voter) > 3 else 0}, {voter[4] if len(voter) > 4 else 0}, '{voter[5] if len(voter) > 5 else ''}', '{voter[6] if len(voter) > 6 else ''}')"
    print(f'  Inserting voter: {voter[0]} - {voter[1]}')
    turso_execute(sql)

print()
print('=' * 50)
print('Seeding complete!')

# Verify
print()
print('Verifying Turso data...')
for table in ['admins', 'election_officials', 'positions', 'candidates', 'voters']:
    result = turso_execute(f'SELECT COUNT(*) FROM {table}')
    if result:
        count = result[0][0] if isinstance(result, list) and result else '?'
        print(f'{table}: {count} records')
    else:
        print(f'{table}: Error reading')

sqlite_conn.close()
if 'turso_conn' in locals():
    turso_conn.close()

import sqlite3
conn = sqlite3.connect('voting.db')
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='voters'")
result = cursor.fetchone()
if result:
    print(result[0])
else:
    print("No voters table")
conn.close()
import sqlite3

conn = sqlite3.connect('votechain.db')
cursor = conn.cursor()

# Update existing rows to have empty phone_number
cursor.execute('UPDATE voters SET phone_number = "" WHERE phone_number IS NULL')
conn.commit()

# Verify
cursor.execute('SELECT resident_id, phone_number FROM voters LIMIT 5')
for row in cursor.fetchall():
    print(row)

print('Fixed NULL phone_numbers')
conn.close()
print('Done!')
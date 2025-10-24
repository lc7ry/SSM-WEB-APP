import sqlite3

conn = sqlite3.connect('carmeet_community.db')
cursor = conn.cursor()

print("=== Database Debug Info ===")

# Check pragmas
cursor.execute("PRAGMA journal_mode;")
print(f"Journal mode: {cursor.fetchone()[0]}")

cursor.execute("PRAGMA synchronous;")
print(f"Synchronous: {cursor.fetchone()[0]}")

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables: {[t[0] for t in tables]}")

# Check members
cursor.execute("SELECT COUNT(*) FROM members")
print(f"Members count: {cursor.fetchone()[0]}")

cursor.execute("SELECT MemberID, Username, Email FROM members")
members = cursor.fetchall()
print("Members:")
for m in members:
    print(f"  {m}")

conn.close()

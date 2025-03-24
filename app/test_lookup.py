import sqlite3

conn = sqlite3.connect("vessel_flags.db")
cursor = conn.cursor()
for row in cursor.execute("SELECT * FROM vessel_flags"):
    print(row)
conn.close()

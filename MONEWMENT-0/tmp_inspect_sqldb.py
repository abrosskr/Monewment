import sqlite3
import os

db_path = "C:/monewment/PHYSICS/PHYSICS-1/local_registry.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    for table_name in [t[0] for t in tables]:
        cursor.execute(f"PRAGMA table_info({table_name});")
        print(f"Schema for {table_name}:", cursor.fetchall())
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        print(f"Count for {table_name}:", cursor.fetchone()[0])
    conn.close()
else:
    print("File not found")

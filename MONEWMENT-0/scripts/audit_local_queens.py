import sqlite3
import os
from pathlib import Path

def check_local_db(db_path):
    if not os.path.exists(db_path):
        print(f"NOT_FOUND: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM local_registry WHERE entity_type='QUEEN'").fetchall()
        print(f"DATABASE: {db_path}")
        print(f"QUEEN_COUNT: {len(rows)}")
        for row in rows:
            print(f"  - ID: {row['id']}, status: {row['status']}, last_seen: {row['last_seen_at']}")
        conn.close()
    except Exception as e:
        print(f"ERROR reading {db_path}: {e}")

if __name__ == "__main__":
    bases = [
        r"C:\monewment\PHYSICS\PHYSICS-1",
        r"C:\monewment\PHYSICS\PHYSICS-2",
        r"C:\monewment\PHYSICS\PHYSICS-3",
        r"C:\monewment\AREUM\AREUM-3",
        r"C:\monewment\AREUM\AREUM-FORAGER-1"
    ]
    for b in bases:
        db = os.path.join(b, "local_registry.db")
        check_local_db(db)

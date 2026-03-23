import sqlite3
import os

def inspect_local_schema(db_path):
    if not os.path.exists(db_path):
        print(f"NOT_FOUND: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("PRAGMA table_info(local_registry)")
        cols = cursor.fetchall()
        print(f"SCHEMA for {db_path}:")
        for col in cols:
            print(f"  Col: {col[1]}, Type: {col[2]}")
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    inspect_local_schema(r"C:\monewment\PHYSICS\PHYSICS-1\local_registry.db")

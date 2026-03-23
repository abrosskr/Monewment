import sqlite3
import os

def check_local_db(db_path):
    if not os.path.exists(db_path):
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM local_registry WHERE entity_type='QUEEN'").fetchall()
        if rows:
            print(f"DATABASE: {db_path}")
            print(f"QUEEN_COUNT: {len(rows)}")
            for row in rows:
                print(f"  - ID: {row['entity_id']}, status: {row['status']}, last_seen: {row.get('last_heartbeat', 'N/A')}")
        conn.close()
    except Exception as e:
        print(f"ERROR reading {db_path}: {e}")

if __name__ == "__main__":
    # Scan PHYSICS and AREUM directories
    root = r"C:\monewment"
    for domain in ["PHYSICS", "AREUM"]:
        domain_path = os.path.join(root, domain)
        if not os.path.exists(domain_path): continue
        for entry in os.listdir(domain_path):
            epath = os.path.join(domain_path, entry)
            if os.path.isdir(epath):
                db = os.path.join(epath, "local_registry.db")
                check_local_db(db)

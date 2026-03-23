import sqlite3
import os
import uuid

def fix_local_ids(db_path, primary_queen_id):
    if not os.path.exists(db_path): return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Check all entities
        rows = conn.execute("SELECT * FROM local_registry").fetchall()
        print(f"Checking DB: {db_path}")
        
        for row in rows:
            eid = row['entity_id']
            etype = row['entity_type']
            print(f"  Found {etype}: {eid}")
            
            # If it's a QUEEN and not our primary UUID, fix it
            if etype == 'QUEEN' and eid != primary_queen_id:
                print(f"    [FIX] Changing non-standard QUEEN ID {eid} -> {primary_queen_id}")
                conn.execute("UPDATE local_registry SET entity_id = ? WHERE entity_id = ?", (primary_queen_id, eid))
            
            # If ANY ID is not a UUID, and we don't have a replacement, we should probably skip or fix
            try:
                uuid.UUID(str(eid))
            except ValueError:
                if etype != 'QUEEN': # We already handled Queen
                    new_id = str(uuid.uuid4())
                    print(f"    [FIX] Changing non-UUID {etype} ID {eid} -> {new_id}")
                    conn.execute("UPDATE local_registry SET entity_id = ? WHERE entity_id = ?", (new_id, eid))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    PRIMARY_QUEEN_ID = 'ba537759-f607-4eda-841c-eeba65a5147b'
    fix_local_ids(r"C:\monewment\PHYSICS\PHYSICS-1\local_registry.db", PRIMARY_QUEEN_ID)
    fix_local_ids(r"C:\monewment\AREUM\AREUM-1\local_registry.db", PRIMARY_QUEEN_ID)

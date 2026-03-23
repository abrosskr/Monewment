import psycopg
import sys

sys.path.append(r"c:\monewment\MONEWMENT-0")
from core.database import engine

import psycopg
import sys
import uuid

sys.path.append(r"c:\monewment\MONEWMENT-0")
from core.database import engine

def trigger_test():
    # Convert SQLAlchemy URL to psycopg URL format
    db_url = str(engine.url).replace("postgresql+asyncpg", "postgresql")
    
    print(f"Connecting to {db_url}...")
    with psycopg.connect(db_url, autocommit=True) as conn:
        print("Inserting fake data to trigger SENTINEL via actual DB Triggers...")
        # 1. Trigger AREUM by inserting into assets
        try:
            fake_hash_1 = str(uuid.uuid4())
            conn.execute(f"""
                INSERT INTO schema_stratum_STRATUM_1.assets (hash, pipeline_state) 
                VALUES ('{fake_hash_1}', 'RAW_DUMPED');
            """)
            print("- Inserted into assets -> AREUM should awake.")
        except Exception as e:
            print(f"Error inserting asset: {e}")

        # 2. Trigger PHYSICS by inserting into cross_reports
        try:
            conn.execute(f"""
                INSERT INTO schema_pipeline.cross_reports (stratum_id, summary, confidence_score) 
                VALUES ('{uuid.uuid4()}', 'TEST', 0.99);
            """)
            print("- Inserted into cross_reports -> PHYSICS should awake.")
        except Exception as e:
            print(f"Error inserting report: {e}")

if __name__ == "__main__":
    trigger_test()

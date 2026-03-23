import sys
import uuid
import psycopg
from pathlib import Path

# Path resolution for MONEWMENT-0 core
sys.path.append(r"c:\monewment\MONEWMENT-0")

from core.database import engine

DB_URL = str(engine.url).replace("postgresql+asyncpg", "postgresql")

def test_pim_trigger():
    # A highly unstructured, ambiguous string testing the VAS Extraction
    raw_test_string = "지리산 흑도야지 냉장 무항생제 앞다리살 500g 찌개용"
    
    print(f"Injecting test string: '{raw_test_string}'")
    
    try:
        with psycopg.connect(DB_URL, autocommit=True) as conn:
            # Insert into STRATUM-1 to fire the trigger
            asset_hash = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO schema_stratum_STRATUM_1.assets (vendor_id, raw_data, hash, pipeline_state)
                VALUES (
                    (SELECT id FROM schema_stratum_STRATUM_1.vendors LIMIT 1),
                    %s,
                    %s,
                    'RAW_DUMPED'
                )
            """, (raw_test_string, asset_hash))
            print("Successfully inserted raw asset. Sentinel should now ignite AREUM-IN-1.")
    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    test_pim_trigger()

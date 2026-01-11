
import sys
import os
from sqlalchemy import create_engine, text

def fix_schema():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "monewment.db")
    engine = create_engine(f"sqlite:///{db_path}")
    
    print(f"🔧 Fixing Schema for {db_path}...")
    
    with engine.connect() as conn:
        # Check if 'status' column exists in 'projects'
        # SQLite pragma
        result = conn.execute(text("PRAGMA table_info(projects)")).fetchall()
        columns = [row[1] for row in result]
        
        if 'status' not in columns:
            print("⚠️ Column 'status' missing in 'projects'. Adding it...")
            try:
                conn.execute(text("ALTER TABLE projects ADD COLUMN status VARCHAR DEFAULT 'ACTIVE'"))
                conn.commit()
                print("✅ Added 'status' column.")
            except Exception as e:
                print(f"❌ Failed to add column: {e}")
        else:
            print("✅ 'status' column already exists.")
            
        # Also check 'installed_features' just in case
        if 'installed_features' not in columns:
             print("⚠️ Column 'installed_features' missing in 'projects'. Adding it...")
             try:
                # SQLite doesn't support adding JSON column type explicitly in syntax usually, just TEXT or similar, but JSON is valid in recent versions or just treat as text
                conn.execute(text("ALTER TABLE projects ADD COLUMN installed_features JSON DEFAULT '[\"logs\"]'"))
                conn.commit()
                print("✅ Added 'installed_features' column.")
             except Exception as e:
                print(f"❌ Failed to add column: {e}")

if __name__ == "__main__":
    fix_schema()

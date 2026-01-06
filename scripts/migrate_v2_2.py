
from sqlalchemy import create_engine, text
from src.config import settings

# DB 주소 (local forward port 5433 사용 중일 것으로 예상)
DB_URL = "postgresql://user:monewment1234@localhost:5433/monewment"

def migrate():
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        print("🛠️ Starting Migration v2.2 (Hierarchy & Quotas)...")
        
        # 1. Create clusters table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS clusters (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                region VARCHAR(100) DEFAULT 'kr-seoul-1',
                status VARCHAR(50) DEFAULT 'ACTIVE',
                cpu_capacity INTEGER DEFAULT 100,
                ram_capacity_gb INTEGER DEFAULT 512,
                gpu_capacity INTEGER DEFAULT 8
            )
        """))
        print("✅ clusters table verified")

        # 2. Add columns to organizations
        alter_orgs = [
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS cluster_id INTEGER REFERENCES clusters(id)",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS quota_cpu INTEGER DEFAULT 10",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS quota_ram_gb INTEGER DEFAULT 32",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS quota_gpu INTEGER DEFAULT 0",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'ACTIVE'"
        ]
        for cmd in alter_orgs:
            try:
                conn.execute(text(cmd))
                print(f"✅ {cmd.split('ADD COLUMN')[1].strip()}")
            except Exception as e:
                print(f"⚠️ Skipping/Error: {e}")

        # 3. Add columns to projects
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'ACTIVE'"))
            print("✅ projects.status added")
        except Exception as e:
            print(f"⚠️ Skipping/Error: {e}")

        conn.commit()
        print("\n🚀 Migration v2.2 Complete!")

if __name__ == "__main__":
    migrate()

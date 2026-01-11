
from sqlalchemy import create_engine, text
from src.config import settings

def migrate():
    # Helper to fix SQLAlchemy URL for Sync execution if needed, but we can reuse what works
    url = str(settings.SQLALCHEMY_DATABASE_URI)
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "")
    
    print(f"Connecting to {url}...")
    engine = create_engine(url)
    
    with engine.connect() as conn:
        print("Migrating table 'project_subscriptions'...")
        try:
            conn.execute(text("ALTER TABLE project_subscriptions ADD COLUMN allow_burst BOOLEAN DEFAULT FALSE"))
            print(" - Added 'allow_burst'")
        except Exception as e:
            print(f" - allow_burst: {e}")

        try:
            conn.execute(text("ALTER TABLE project_subscriptions ADD COLUMN burst_multiplier NUMERIC(4, 2) DEFAULT 1.5"))
            print(" - Added 'burst_multiplier'")
        except Exception as e:
            print(f" - burst_multiplier: {e}")
            
        conn.commit()
    print("Migration Complete.")

if __name__ == "__main__":
    migrate()

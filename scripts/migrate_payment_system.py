
from sqlalchemy import create_engine, text, inspect
from src.config import settings

def migrate():
    # Helper to fix SQLAlchemy URL for Sync execution
    url = str(settings.SQLALCHEMY_DATABASE_URI)
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "")
    
    print(f"Connecting to {url}...")
    engine = create_engine(url)
    
    with engine.connect() as conn:
        print("Migrating Payment System schema...")
        
        # 1. Add prepaid_credits to project_budgets
        try:
            conn.execute(text("ALTER TABLE project_budgets ADD COLUMN prepaid_credits NUMERIC(10, 2) DEFAULT 0.00"))
            print(" - Added 'prepaid_credits' to project_budgets")
        except Exception as e:
            print(f" - prepaid_credits: {e}")

        # 2. Create payment_history table
        # We use raw SQL for simplicity in this migration script, or we could use Alembic properly.
        # But keeping with the 'script' pattern:
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS payment_history (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER REFERENCES projects(id),
                    transaction_id VARCHAR UNIQUE,
                    amount NUMERIC(10, 2) NOT NULL,
                    currency VARCHAR DEFAULT 'USD',
                    status VARCHAR DEFAULT 'SUCCESS',
                    payment_method VARCHAR,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """))
            print(" - Created 'payment_history' table")
        except Exception as e:
            print(f" - payment_history: {e}")
            
        conn.commit()
    print("Migration Complete.")

if __name__ == "__main__":
    migrate()

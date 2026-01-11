
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Bypass config validation for schema update
from src.models import Base, SubscriptionPlan, VMFlavor, AIModel
from src.config import settings

def get_db_session():
    # Construct Sync URL (using default driver, likely psycopg2)
    db_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    print(f"🔌 Connecting to {db_url}...")
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    return engine, SessionLocal()

def init_metering_db():
    engine, db = get_db_session()

    # Create tables
    print("🛠️  Creating tables if not exist...")
    Base.metadata.create_all(engine)
    
    # Seed Data
    print("🌱 Seeding initial data...")
    
    # 1. Plans
    if not db.query(SubscriptionPlan).count():
        plans = [
            SubscriptionPlan(name="Starter", price=0.00, monthly_credits=5.00),
            SubscriptionPlan(name="Pro", price=50.00, monthly_credits=60.00),
            SubscriptionPlan(name="Enterprise", price=200.00, monthly_credits=250.00),
        ]
        db.add_all(plans)
        print("   - Added Subscription Plans")

    # 2. VM Flavors
    if not db.query(VMFlavor).count():
        flavors = [
            VMFlavor(name="Micro", channel="GENERAL", spec_tier="LOW", cpu_cores=1, memory_gb=2, hourly_rate=0.02),
            VMFlavor(name="Gaming Std", channel="GAMING", spec_tier="MID", cpu_cores=4, memory_gb=16, gpu_model="GTX 1060", hourly_rate=0.50),
            VMFlavor(name="AI Research", channel="RND", spec_tier="HIGH", cpu_cores=8, memory_gb=32, gpu_model="A10G", hourly_rate=2.50),
        ]
        db.add_all(flavors)
        print("   - Added VM Flavors")

    # 3. AI Models
    if not db.query(AIModel).count():
        models = [
            AIModel(name="GPT-4-Turbo", hourly_surcharge=1.00),
            AIModel(name="Claude-3-Opus", hourly_surcharge=1.50),
            AIModel(name="Llama-3-70B", hourly_surcharge=0.50),
        ]
        db.add_all(models)
        print("   - Added AI Models")

    db.commit()
    db.close()
    print("✅ Metering DB Initialized!")

if __name__ == "__main__":
    init_metering_db()


import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import SessionLocal, engine
from src.models import Base, SubscriptionPlan, VMFlavor, AIModel
from sqlalchemy.orm import Session
from decimal import Decimal

def seed_data():
    db = SessionLocal()
    try:
        print("🌱 Seeding Billing Data...")
        
        # 1. Seed Subscription Plans
        if not db.query(SubscriptionPlan).first():
            print("   - Creating Subscription Plans")
            plans = [
                SubscriptionPlan(name="Starter", price=0.00, monthly_credits=5.00, allowed_flavors=["mid-gaming", "mid-rnd"]),
                SubscriptionPlan(name="Pro", price=50.00, monthly_credits=100.00, allowed_flavors=["all"]),
                SubscriptionPlan(name="Enterprise", price=200.00, monthly_credits=500.00, allowed_flavors=["all"]),
            ]
            db.add_all(plans)
        
        # 2. Seed VM Flavors (Hardware)
        if not db.query(VMFlavor).first():
            print("   - Creating VM Flavors (Hardware)")
            flavors = [
                # Gaming Channel
                VMFlavor(name="Gaming Std", channel="GAMING", spec_tier="MID", cpu_cores=4, memory_gb=8, gpu_model="GTX 1660", hourly_rate=0.50),
                VMFlavor(name="Gaming Pro", channel="GAMING", spec_tier="HIGH", cpu_cores=8, memory_gb=16, gpu_model="RTX 4090", hourly_rate=2.50),
                
                # R&D Channel
                VMFlavor(name="Dev Basic", channel="RND", spec_tier="MID", cpu_cores=2, memory_gb=4, gpu_model=None, hourly_rate=0.20),
                VMFlavor(name="AI Workstation", channel="RND", spec_tier="HIGH", cpu_cores=16, memory_gb=32, gpu_model="A100", hourly_rate=4.00),
            ]
            db.add_all(flavors)
            
        # 3. Seed AI Models (Software)
        if not db.query(AIModel).first():
            print("   - Creating AI Models (Software)")
            models = [
                AIModel(name="Llama-3-8B (Open)", hourly_surcharge=0.00),
                AIModel(name="Llama-3-70B (Open)", hourly_surcharge=0.50),
                AIModel(name="GPT-4-Turbo (Commercial)", hourly_surcharge=2.00),
            ]
            db.add_all(models)

        db.commit()
        print("✅ Seeding Complete.")
        
    except Exception as e:
        print(f"❌ Seeding Failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables exist
    print("🔄 Checking/Creating Tables...")
    Base.metadata.create_all(bind=engine)
    seed_data()

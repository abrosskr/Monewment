
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal
from src.models import Cluster, Organization, Project, User, UserRole
from src.core.security import hash_password

def seed_hierarchy():
    db = SessionLocal()
    try:
        # 1. Cluster 생성
        cluster = db.query(Cluster).filter(Cluster.name == "Main-Cluster-01").first()
        if not cluster:
            cluster = Cluster(
                name="Main-Cluster-01",
                region="kr-seoul-1",
                cpu_capacity=200,
                ram_capacity_gb=1024,
                gpu_capacity=16
            )
            db.add(cluster)
            db.flush()
            print("✅ Cluster created")

        # 2. Organization 생성 (Monewment Group)
        org = db.query(Organization).filter(Organization.name == "Monewment Group").first()
        if not org:
            org = Organization(
                name="Monewment Group",
                plan_type="team",
                cluster_id=cluster.id,
                quota_cpu=100,
                quota_ram_gb=512,
                quota_gpu=4,
                status="ACTIVE"
            )
            db.add(org)
            db.flush()
            print("✅ Organization created")

        # 3. Projects 생성 (Top-Down Example)
        p1_name = "PCRoom-Service"
        p2_name = "RND-Lab"
        
        for p_name in [p1_name, p2_name]:
            proj = db.query(Project).filter(Project.name == p_name).first()
            if not proj:
                proj = Project(
                    name=p_name,
                    org_id=org.id,
                    status="ACTIVE"
                )
                db.add(proj)
                print(f"✅ Project {p_name} created")

        # 4. Super Admin User (if not exists)
        admin_email = "monewment@admin.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
                org_id=org.id
            )
            db.add(admin)
            print("✅ Super Admin User created")

        db.commit()
        print("\n🚀 Hierarchy Seeding Complete!")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_hierarchy()

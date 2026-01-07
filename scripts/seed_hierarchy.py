
import sys
import os
import asyncio
from sqlalchemy import select

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import AsyncSessionLocal
from src.models import Cluster, Organization, Project, User, UserRole
from src.core.security import hash_password

async def seed_hierarchy():
    async with AsyncSessionLocal() as db:
        try:
            # 1. Cluster 생성
            result = await db.execute(select(Cluster).filter(Cluster.name == "Main-Cluster-01"))
            cluster = result.scalars().first()
            
            if not cluster:
                cluster = Cluster(
                    name="Main-Cluster-01",
                    region="kr-seoul-1",
                    cpu_capacity=200,
                    ram_capacity_gb=1024,
                    gpu_capacity=16
                )
                db.add(cluster)
                await db.flush()
                print("✅ Cluster created")

            # 2. Organization 생성 (Monewment Group)
            result = await db.execute(select(Organization).filter(Organization.name == "Monewment Group"))
            org = result.scalars().first()
            
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
                await db.flush()
                print("✅ Organization created")

            # 3. Projects 생성 (Top-Down Example)
            p1_name = "PCRoom-Service"
            p2_name = "RND-Lab"
            
            for p_name in [p1_name, p2_name]:
                result = await db.execute(select(Project).filter(Project.name == p_name))
                proj = result.scalars().first()
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
            result = await db.execute(select(User).filter(User.email == admin_email))
            admin = result.scalars().first()
            
            if not admin:
                admin = User(
                    email=admin_email,
                    hashed_password=hash_password("admin123"),
                    role=UserRole.ADMIN,
                    org_id=org.id
                )
                db.add(admin)
                print("✅ Super Admin User created")
            else:
                # [안전장치] 비밀번호 무조건 초기화 (테스트용)
                admin.hashed_password = hash_password("admin123")
                print("♻️ Admin Password Reset to 'admin123'")

            await db.commit()
            print("\n🚀 Hierarchy Seeding Complete!")
            
        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(seed_hierarchy())

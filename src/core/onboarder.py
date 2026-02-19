from typing import List, Dict
from sqlalchemy import text
from src.core.database import engine
from src.core.provisioner import Provisioner
from src.core.migrator import GlobalMigrator

class TenantOnboarder:
    @staticmethod
    async def onboard_tenant(queen_id: str, initial_members: List[Dict[str, str]]):
        """
        [입주 프로세스]
        1. 물리적 방 생성 (Provisioning)
        2. 최신 스키마 적용 (Migration)
        3. 초기 데이터 적재 (Bulk Insert)
        """
        report = {"queen_id": queen_id, "steps": {}}

        # Step 1: 기초 공사
        await Provisioner.provision_queen_room(queen_id)
        report["steps"]["provision"] = "success"

        # Step 2: 문명 동기화 (V1, V2 등 최신 상태로)
        await GlobalMigrator.upgrade_all()
        report["steps"]["migration"] = "success"

        # Step 3: 초기 데이터 적재
        try:
            async with engine.begin() as conn:
                await conn.execute(text(f"SET LOCAL search_path TO queen_{queen_id}"))
                
                if initial_members:
                    query = text("""
                        INSERT INTO members (username, email, phone_number) 
                        VALUES (:username, :email, :phone_number)
                    """)
                    await conn.execute(query, initial_members)
                
                report["steps"]["data_import"] = f"{len(initial_members)} members imported"
        except Exception as e:
            report["steps"]["data_import"] = f"failed: {str(e)}"

        return report
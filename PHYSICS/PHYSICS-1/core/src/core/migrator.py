from sqlalchemy import text
from src.core.database import engine

class GlobalMigrator:
    # [GMP 규약] 마이그레이션 설계도: 번호가 높을수록 최신 버전입니다.
    MIGRATIONS = {
        1: "ALTER TABLE members ADD COLUMN IF NOT EXISTS email VARCHAR(255);",
        2: "ALTER TABLE members ADD COLUMN IF NOT EXISTS phone_number VARCHAR(50);",
        # 새로운 변경사항이 생기면 여기에 3, 4... 순서대로 추가만 하세요.
    }

    @staticmethod
    async def get_all_queens():
        """DB 내 모든 'queen_' 테넌트 스키마 목록을 조회합니다."""
        async with engine.connect() as conn:
            query = text("SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'queen_%'")
            result = await conn.execute(query)
            return [row[0] for row in result]

    @staticmethod
    async def ensure_history_table(conn, schema: str):
        """각 테넌트 방에 마이그레이션 이력 관리용 테이블이 있는지 확인합니다."""
        await conn.execute(text(f"SET LOCAL search_path TO {schema}"))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS migration_history (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))

    @staticmethod
    async def get_applied_versions(conn):
        """현재 테넌트에 이미 적용된 마이그레이션 버전들을 가져옵니다."""
        result = await conn.execute(text("SELECT version FROM migration_history"))
        return {row[0] for row in result}

    @staticmethod
    async def upgrade_all():
        """
        [GMP 실행] 모든 테넌트 방을 전수 조사하여 
        아직 적용되지 않은 최신 버전까지 자동으로 순차 업데이트합니다.
        """
        queens = await GlobalMigrator.get_all_queens()
        report = {"total": len(queens), "upgraded": [], "already_latest": [], "failed": []}

        for schema in queens:
            try:
                async with engine.begin() as conn:
                    # 1. 이력 테이블 생성 확인
                    await GlobalMigrator.ensure_history_table(conn, schema)
                    
                    # 2. 미적용 버전 필터링
                    applied = await GlobalMigrator.get_applied_versions(conn)
                    pending = sorted([v for v in GlobalMigrator.MIGRATIONS if v not in applied])
                    
                    if not pending:
                        report["already_latest"].append(schema)
                        continue

                    # 3. 순차적 업데이트 (V1 -> V2 -> ...)
                    for v in pending:
                        await conn.execute(text(GlobalMigrator.MIGRATIONS[v]))
                        await conn.execute(text("INSERT INTO migration_history (version) VALUES (:v)"), {"v": v})
                    
                    report["upgraded"].append({"schema": schema, "versions": pending})
            except Exception as e:
                report["failed"].append({"schema": schema, "error": str(e)})
        
        return report
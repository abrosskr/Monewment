import re
from sqlalchemy import text
from src.core.database import async_session_factory

class Provisioner:
    @staticmethod
    async def provision_queen_room(queen_id: str):
        # 1. Security: Strict Input Validation (Zero-Trust)
        # Allows only lowercase alphanumeric and underscore, 3-30 chars.
        if not re.match(r"^[a-z0-9_]{3,30}$", queen_id):
            raise ValueError(f"Invalid Queen ID format: {queen_id}. Must match ^[a-z0-9_]{3,30}$")

        schema_name = f"queen_{queen_id}"
        role_name = f"role_{queen_id}"

        async with async_session_factory() as session:
            async with session.begin():
                # 2. Schema Creation
                await session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))

                # 3. Role Creation (Idempotent via DO block)
                create_role_sql = f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{role_name}') THEN
                        CREATE ROLE {role_name} NOLOGIN;
                    END IF;
                END
                $$;
                """
                await session.execute(text(create_role_sql))

                # 4. [CRITICAL FIX] Grant Role Membership to postgres
                # 관리자 계정이 이 Role로 변신(SET ROLE)할 수 있도록 권한을 상속시킵니다.
                await session.execute(text(f"GRANT {role_name} TO postgres"))

                # 5. Grant Privileges on Schema
                await session.execute(text(f"GRANT USAGE, CREATE ON SCHEMA {schema_name} TO {role_name}"))
                await session.execute(text(f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT ALL ON TABLES TO {role_name}"))

                # 6. Base Table Creation (Members)
                # 스키마 내부의 테이블이 실제 물리적으로 생성되어야 API가 500 에러를 뱉지 않습니다.
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.members (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
                """
                await session.execute(text(create_table_sql))
                
                # 7. Table-level Privileges (Double-Check)
                # 생성된 테이블에 대해 Role이 모든 권한을 갖도록 확정합니다.
                await session.execute(text(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {schema_name} TO {role_name}"))
                await session.execute(text(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA {schema_name} TO {role_name}"))
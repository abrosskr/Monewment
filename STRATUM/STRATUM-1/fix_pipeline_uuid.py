import asyncio

from sqlalchemy import text

from core.database import AsyncSessionLocal



async def fix_pipeline_uuid_types():

    """

    [V51.5] MIGRATION: UUID to TEXT Casting for Pipeline Schema

    Resolves 'operator does not exist: uuid = text' 500 errors.

    """

    async with AsyncSessionLocal() as db:

        try:

            print("[*] Initiating Pipeline UUID -> TEXT Migration...")

            

            # 1. intelligence_reports: stratum_id

            await db.execute(text("""

                ALTER TABLE schema_pipeline.intelligence_reports 

                ALTER COLUMN stratum_id TYPE TEXT USING stratum_id::TEXT;

            """))

            print("[v] intelligence_reports.stratum_id: Cast to TEXT.")



            # 2. strategic_decrees: decree_id

            await db.execute(text("""

                ALTER TABLE schema_pipeline.strategic_decrees 

                ALTER COLUMN decree_id TYPE TEXT USING decree_id::TEXT;

            """))

            print("[v] strategic_decrees.decree_id: Cast to TEXT.")



            # 3. strategic_decrees: stratum_id

            await db.execute(text("""

                ALTER TABLE schema_pipeline.strategic_decrees 

                ALTER COLUMN stratum_id TYPE TEXT USING stratum_id::TEXT;

            """))

            print("[v] strategic_decrees.stratum_id: Cast to TEXT.")



            # 4. cross_reports: stratum_id

            await db.execute(text("""

                ALTER TABLE schema_pipeline.cross_reports 

                ALTER COLUMN stratum_id TYPE TEXT USING stratum_id::TEXT;

            """))

            print("[v] cross_reports.stratum_id: Cast to TEXT.")



            await db.commit()

            print("[!] Migration Successful. Commit Complete.")

            

        except Exception as e:

            await db.rollback()

            print(f"[!] Migration Failed: {e}")

            print("[!] Rollback Executed.")

            raise



if __name__ == "__main__":

    asyncio.run(fix_pipeline_uuid_types())
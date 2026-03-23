from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from core.models_pipeline import PipelineTask, TaskStatus
from core.routing_guard import validate_stratum_name, validate_stratum_id_match

class PipelineRepository:
    """Repository for the Supabase State Machine (pipeline_tasks table) and Global REX Pipeline"""

    def __init__(self, db_session: AsyncSession, stratum_name: str | None = None):
        self.db = db_session
        self.stratum_name = validate_stratum_name(stratum_name) if stratum_name else None
        self.schema = f"schema_stratum_{self.stratum_name}" if self.stratum_name else None

    # --- Stratum-Specific Asset Mutation (AREUM) ---
    async def update_asset_areum(self, asset_id: str, areum_data: dict) -> bool:
        """AREUM 분석 결과를 Stratum assets 테이블에 반영 (Mutation)"""
        if not self.schema: raise ValueError("Stratum schema not initialized.")
        
        query = f"""
            UPDATE {self.schema}.assets
            SET ai_summary = :summary,
                essence_tags = :tags,
                ai_confidence = :confidence,
                areum_id = :areum_id,
                areum_processed_at = NOW(),
                pipeline_state = 'AREUM_DONE'
            WHERE id = :asset_id
        """
        await self.db.execute(text(query), {
            "summary": areum_data["ai_summary"],
            "tags": str(areum_data["essence_tags"]),
            "confidence": areum_data["ai_confidence"],
            "areum_id": areum_data["areum_id"],
            "asset_id": asset_id
        })
        return True

    # --- Global Pipeline Reporting (AREUM -> REX) ---
    async def push_cross_report(self, report_data: dict) -> str | None:
        """AREUM의 분석 결과를 글로벌 schema_pipeline.cross_reports 에 적재"""
        query = """
            INSERT INTO schema_pipeline.cross_reports 
            (areum_id, stratum_id, source_asset_id, ollama_model, confidence_score, keywords, summary, raw_essence)
            VALUES (:areum_id, :stratum_id, :asset_id, :model, :confidence, :keywords, :summary, :raw)
            RETURNING report_id
        """
        result = await self.db.execute(text(query), {
            "areum_id": report_data["areum_id"],
            "stratum_id": report_data["stratum_id"],
            "asset_id": report_data.get("source_asset_id"),
            "model": report_data.get("ollama_model"),
            "confidence": report_data["confidence_score"],
            "keywords": str(report_data.get("keywords", [])),
            "summary": report_data["summary"],
            "raw": str(report_data.get("raw_essence", {}))
        })
        row = result.fetchone()
        return str(row[0]) if row else None

    # --- Global Strategic Decrees (REX) ---
    async def get_unconsumed_reports(self, limit: int = 20) -> list[dict]:
        """REX가 아직 융합하지 않은 cross_reports 조회"""
        query = """
            SELECT report_id, areum_id, stratum_id, source_asset_id, confidence_score, keywords, summary
            FROM schema_pipeline.cross_reports
            WHERE rex_consumed = FALSE
            ORDER BY created_at ASC
            LIMIT :limit
        """
        result = await self.db.execute(text(query), {"limit": limit})
        return [dict(r._mapping) for r in result.fetchall()]

    async def push_strategic_decree(self, decree_data: dict) -> str | None:
        """REX의 융합 분석 결과를 전략 교시(Strategic Decree)로 적재"""
        query = """
            INSERT INTO schema_pipeline.strategic_decrees 
            (strategic_directive, focus_sector, correlations, source_ref_ids)
            VALUES (:directive, :sector, :correlations, :source_ids)
            RETURNING decree_id
        """
        result = await self.db.execute(text(query), {
            "directive": decree_data["strategic_directive"],
            "sector": decree_data["focus_sector"],
            "correlations": str(decree_data.get("correlations", [])),
            "source_ids": str(decree_data.get("source_ref_ids", []))
        })
        row = result.fetchone()
        return str(row[0]) if row else None

    async def mark_reports_consumed(self, report_ids: list[str]) -> None:
        """보고서 소비 완료 마킹 (REX 전용)"""
        query = """
            UPDATE schema_pipeline.cross_reports
            SET rex_consumed = TRUE, rex_consumed_at = NOW()
            WHERE report_id = ANY(:ids)
        """
        await self.db.execute(text(query), {"ids": report_ids})

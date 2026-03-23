import os
from pathlib import Path
from .logger import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class RegistryRepository:
    """Entity Registry — 생성/핑/사망/조회"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_next_sequence(self, entity_class: str) -> str:
        """[Absolute Sequencer] 동시성 제어를 통해 안전하게 다음 순번을 발급받음"""
        q = text("""
            UPDATE schema_registry.sequences
            SET current_value = current_value + 1, updated_at = NOW()
            WHERE entity_class = :entity_class
            RETURNING current_value
        """)
        result = await self.db.execute(q, {"entity_class": entity_class})
        row = result.fetchone()
        if not row:
            # 존재하지 않는 클래스라면 방어 코드로 1부터 시작
            await self.db.execute(text("""
                INSERT INTO schema_registry.sequences (entity_class, current_value)
                VALUES (:entity_class, 1) ON CONFLICT DO NOTHING
            """), {"entity_class": entity_class})
            return f"{entity_class}-1"
        return f"{entity_class}-{row.current_value}"

    # ========== BIRTH ==========
    async def birth_monewment(self, payload: dict) -> dict:
        """필수: display_name, owner_user_id / 선택: host_machine_id, core_version"""
        params = {
            "display_name":   payload["display_name"],
            "owner_user_id":  payload["owner_user_id"],
            "host_machine_id": payload.get("host_machine_id"),
            "core_version":   payload.get("core_version"),
        }
        q = text("""
            INSERT INTO schema_registry.monewments
                (display_name, owner_user_id, host_machine_id, core_version)
            VALUES (:display_name, :owner_user_id, :host_machine_id, :core_version)
            RETURNING monewment_id, born_at
        """)
        result = await self.db.execute(q, params)
        row = result.fetchone()
        return {"entity_id": str(row.monewment_id), "born_at": str(row.born_at), "fencing_token": 1}

    async def birth_stratum(self, payload: dict) -> dict:
        """필수: stratum_name, monewment_id / 선택: purpose, schema_pg, cloud_ai_enabled"""
        params = {
            "stratum_name":      payload["stratum_name"],
            "monewment_id":      payload["monewment_id"],
            "purpose":           payload.get("purpose"),
            "schema_pg":         payload.get("schema_pg"),
            "root_path":         payload.get("root_path"),
            "cloud_ai_enabled":  payload.get("cloud_ai_enabled", False),
        }
        q = text("""
            INSERT INTO schema_registry.stratums
                (stratum_name, monewment_id, purpose, schema_pg, root_path, cloud_ai_enabled)
            VALUES (:stratum_name, :monewment_id, :purpose, :schema_pg, :root_path, :cloud_ai_enabled)
            ON CONFLICT (monewment_id, stratum_name) DO NOTHING
            RETURNING stratum_id, born_at
        """)
        result = await self.db.execute(q, params)
        row = result.fetchone()
        if not row:
            # 이미 존재 — 기존 ID 조회
            r2 = await self.db.execute(text("""
                SELECT stratum_id, born_at FROM schema_registry.stratums
                WHERE monewment_id = :mid AND stratum_name = :name
            """), {"mid": params["monewment_id"], "name": params["stratum_name"]})
            row = r2.fetchone()
        return {"entity_id": str(row.stratum_id), "born_at": str(row.born_at), "fencing_token": 1}

    async def birth_queen(self, payload: dict) -> dict:
        """선택: relationship_type, host_ip, api_key_masked. 이름(queen_name)은 서버가 자동 채번함."""
        rel_type = payload.get("relationship_type", "INTERNAL").upper()
        entity_class = "QUEEN-IN" if rel_type == "INTERNAL" else "QUEEN-ALLY"
        
        # [Absolute Sequencer] 고유 이름 발급
        official_name = await self._get_next_sequence(entity_class)
        
        params = {
            "queen_name":        official_name,
            "queen_type":        payload.get("queen_type", "GENERAL"),
            "relationship_type": rel_type,
            "host_ip":           payload.get("host_ip"),
            "api_key_masked":    payload.get("api_key_masked"),
            "stratum_ids":       payload.get("stratum_ids", []),
            "instance_path":     payload.get("instance_path"),
        }
        
        # [Idempotency Guard] Check if path is already claimed
        if params["instance_path"]:
            check_q = text("SELECT queen_id, born_at FROM schema_registry.queens WHERE instance_path = :path LIMIT 1")
            res = await self.db.execute(check_q, {"path": params["instance_path"]})
            row = res.fetchone()
            if row:
                # Re-activate if necessary
                await self.db.execute(text("UPDATE schema_registry.queens SET status = 'ACTIVE', died_at = NULL, death_reason = NULL, last_seen_at = NOW() WHERE queen_id = :eid"), {"eid": row.queen_id})
                await self.db.commit()
                return {"entity_id": str(row.queen_id), "born_at": str(row.born_at), "official_name": official_name, "fencing_token": 1, "is_reused": True}

        q = text("""
            INSERT INTO schema_registry.queens
                (queen_name, relationship_type, queen_type, host_ip, api_key_masked, stratum_ids, instance_path)
            VALUES (:queen_name, :relationship_type, :queen_type, :host_ip, :api_key_masked, :stratum_ids, :instance_path)
            RETURNING queen_id, born_at
        """)
        result = await self.db.execute(q, params)
        row = result.fetchone()
        
        # [MATERIALIZATION] Physical folder creation (Great Migration V39/V40 Compliant)
        try:
            # MONEWMENT-0 내부가 아닌 제국 최상위 루트의 QUEEN 기둥으로 라우팅
            empire_root = Path(__file__).resolve().parent.parent.parent
            if rel_type == "INTERNAL":
                base_dir = empire_root / "QUEEN" / "QUEEN_LIST" / "QUEEN-IN"
            else:
                base_dir = empire_root / "QUEEN" / "QUEEN_LIST" / "QUEEN-ALLY"
            
            queen_dir = base_dir / official_name
            queen_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"[REGISTRY] Physical Materialization SUCCESS: {queen_dir}")
        except Exception as e:
            logger.error(f"[REGISTRY] Physical Materialization FAILED for {official_name}: {e}")

        return {"entity_id": str(row.queen_id), "born_at": str(row.born_at), "official_name": official_name, "fencing_token": 1}

    async def birth_ant(self, payload: dict) -> dict:
        """필수: queen_id, stratum_id / 선택: ant_type, target_url. 이름(ant_name)은 자동 채번함."""
        ant_type = payload.get("ant_type", "CODE").upper()
        entity_class = f"ANT-{ant_type}"
        
        # [Absolute Sequencer] 고유 이름 발급
        official_name = await self._get_next_sequence(entity_class)
        
        params = {
            "ant_name":      official_name,
            "queen_id":      payload["queen_id"],
            "stratum_id":    payload["stratum_id"],
            "ant_type":      ant_type,
            "target_url":    payload.get("target_url"),
            "instance_path": payload.get("instance_path"),
        }
        
        # [Idempotency Guard] Check if path is already claimed
        if params["instance_path"]:
            check_q = text("SELECT ant_id, born_at FROM schema_registry.ants WHERE instance_path = :path LIMIT 1")
            res = await self.db.execute(check_q, {"path": params["instance_path"]})
            row = res.fetchone()
            if row:
                # Re-activate
                await self.db.execute(text("UPDATE schema_registry.ants SET status = 'ACTIVE', died_at = NULL, death_reason = NULL, last_seen_at = NOW() WHERE ant_id = :eid"), {"eid": row.ant_id})
                await self.db.commit()
                return {"entity_id": str(row.ant_id), "born_at": str(row.born_at), "official_name": official_name, "fencing_token": 1, "is_reused": True}

        q = text("""
            INSERT INTO schema_registry.ants
                (ant_name, queen_id, stratum_id, ant_type, target_url, instance_path)
            VALUES (:ant_name, :queen_id, :stratum_id, :ant_type, :target_url, :instance_path)
            ON CONFLICT (stratum_id, ant_name) DO NOTHING
            RETURNING ant_id, born_at
        """)
        result = await self.db.execute(q, params)
        row = result.fetchone()
        if not row:
            r2 = await self.db.execute(text("""
                SELECT ant_id, born_at FROM schema_registry.ants
                WHERE stratum_id = :sid AND ant_name = :name
            """), {"sid": params["stratum_id"], "name": params["ant_name"]})
            row = r2.fetchone()
        return {"entity_id": str(row.ant_id), "born_at": str(row.born_at), "official_name": official_name, "fencing_token": 1}

    async def birth_areum(self, payload: dict) -> dict:
        """필수: stratum_id, queen_id / 선택: is_ally, ollama_model. 이름은 자동 채번됨."""
        is_ally = payload.get("is_ally", False)
        entity_class = "AREUM-ALLY" if is_ally else "AREUM-IN"
        
        # [Absolute Sequencer] 고유 이름 발급
        official_name = await self._get_next_sequence(entity_class)
        
        params = {
            "areum_name":    official_name,
            "stratum_id":    payload["stratum_id"],
            "queen_id":      payload["queen_id"],
            "ollama_model":  payload.get("ollama_model", "gemma3:4b"),
            "instance_path": payload.get("instance_path"),
        }
        
        # [Idempotency Guard] Check if path is already claimed
        if params["instance_path"]:
            check_q = text("SELECT areum_id, born_at FROM schema_registry.areums WHERE instance_path = :path LIMIT 1")
            res = await self.db.execute(check_q, {"path": params["instance_path"]})
            row = res.fetchone()
            if row:
                # Re-activate
                await self.db.execute(text("UPDATE schema_registry.areums SET status = 'ACTIVE', died_at = NULL, death_reason = NULL, last_seen_at = NOW() WHERE areum_id = :eid"), {"eid": row.areum_id})
                await self.db.commit()
                return {"entity_id": str(row.areum_id), "born_at": str(row.born_at), "official_name": official_name, "fencing_token": 1, "is_reused": True}

        q = text("""
            INSERT INTO schema_registry.areums
                (areum_name, stratum_id, queen_id, ollama_model, instance_path)
            VALUES (:areum_name, :stratum_id, :queen_id, :ollama_model, :instance_path)
            RETURNING areum_id, born_at
        """)
        
        result = await self.db.execute(q, params)
        row = result.fetchone()
        areum_id = row.areum_id

        # [SYNCHRONIZATION] Dual-insert into areum_registry (V51.5 Pipeline Requirement)
        # This addresses the FK constraint in schema_pipeline.cross_reports
        try:
            await self.db.execute(text("""
                INSERT INTO schema_pipeline.areum_registry
                    (areum_id, areum_name, stratum_id, queen_id, ollama_model, status, born_at, last_seen_at)
                VALUES
                    (:aid, :name, :sid, :qid, :model, 'ACTIVE', :born, NOW())
                ON CONFLICT (areum_id) DO NOTHING
            """), {
                "aid": areum_id,
                "name": official_name,
                "sid": str(params["stratum_id"]),
                "qid": str(params["queen_id"]),
                "model": params["ollama_model"],
                "born": row.born_at
            })
            logger.info(f"[REGISTRY] Sync-Insert for AREUM {areum_id} into pipeline registry SUCCESS.")
        except Exception as e:
            logger.warning(f"[REGISTRY] Sync-Insert for AREUM {areum_id} into pipeline registry FAILED: {e}")

        return {"entity_id": str(areum_id), "born_at": str(row.born_at), "official_name": official_name, "fencing_token": 1}

    # ========== PING (heartbeat) — 레거시; router가 직접 SQL 실행으로 대체됨 ==========
    async def ping(self, entity_type: str, entity_id: str) -> None:
        table_map = {
            "monewment": ("schema_registry.monewments", "monewment_id"),
            "stratum":   ("schema_registry.stratums", "stratum_id"),
            "queen":     ("schema_registry.queens", "queen_id"),
            "ant":       ("schema_registry.ants", "ant_id"),
        }
        table, pk = table_map[entity_type]
        await self.db.execute(text(f"""
            UPDATE {table} SET last_seen_at = NOW() WHERE {pk} = :eid
        """), {"eid": entity_id})

    # ========== DEATH ==========
    async def death(self, entity_type: str, entity_id: str) -> None:
        table_map = {
            "monewment": ("schema_registry.monewments", "monewment_id"),
            "stratum":   ("schema_registry.stratums", "stratum_id"),
            "queen":     ("schema_registry.queens", "queen_id"),
            "ant":       ("schema_registry.ants", "ant_id"),
        }
        table, pk = table_map[entity_type]
        await self.db.execute(text(f"""
            UPDATE {table}
            SET status = 'DEAD', died_at = NOW()
            WHERE {pk} = :eid
        """), {"eid": entity_id})

    # ========== LIST (CCTV sync 호환) ==========
    async def list_queens(self) -> list[dict]:
        result = await self.db.execute(text("""
            SELECT queen_id, queen_name, relationship_type, queen_type,
                   active_ant_count, total_tasks_completed, host_ip, status,
                   born_at, last_seen_at, died_at
            FROM schema_registry.queens ORDER BY born_at DESC
        """))
        return [dict(row._mapping) for row in result.fetchall()]

    async def list_ants(self) -> list[dict]:
        result = await self.db.execute(text("""
            SELECT ant_id, ant_name, queen_id, stratum_id, ant_type, target_url,
                   status, items_collected, payload_hash, born_at, last_seen_at, died_at
            FROM schema_registry.ants ORDER BY born_at DESC
        """))
        return [dict(row._mapping) for row in result.fetchall()]

    async def list_stratums(self) -> list[dict]:
        result = await self.db.execute(text("""
            SELECT stratum_id, stratum_name, status, cloud_ai_enabled,
                   root_path, total_cost_cents, accumulated_cost, budget_limit, 
                   queen_count, born_at, last_seen_at, died_at
            FROM schema_registry.stratums ORDER BY born_at DESC
        """))
        return [dict(row._mapping) for row in result.fetchall()]

    async def list_monewments(self) -> list[dict]:
        result = await self.db.execute(text("""
            SELECT monewment_id, display_name, owner_user_id, status,
                   core_version, total_stratum_count, uptime_seconds,
                   born_at, last_seen_at, died_at
            FROM schema_registry.monewments ORDER BY born_at DESC
        """))
        return [dict(row._mapping) for row in result.fetchall()]

# 📜 Imperial Core Repository — Registry v5.0 (Authoritative ID Injection)
# c:\monewment\STRATUM\STRATUM-1\core\repository_registry.py

import os
from pathlib import Path
from .logger import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from core.config import settings

KST = timezone(timedelta(hours=9))

class RegistryRepository:
    """[MONEWMENT ARCHITECT] Entity Registry — UPSERT 기반 정체성 권위 주입 시스템"""
    VERSION = "IMPERIAL-SURGERY-V100-FINAL"

    def __init__(self, db: AsyncSession):
        self.db = db
        logger.info(f"[REGISTRY-DIAG] Repository Initialized with Version: {self.VERSION}")

    async def _get_next_sequence(self, entity_class: str) -> str:
        now_kst = datetime.now(KST).replace(tzinfo=None)
        q = text("""
            UPDATE schema_registry.sequences
            SET current_value = current_value + 1, updated_at = :now
            WHERE entity_class = :entity_class
            RETURNING current_value
        """)
        result = await self.db.execute(q, {"entity_class": entity_class, "now": now_kst})
        row = result.fetchone()
        if not row:
            await self.db.execute(text("""
                INSERT INTO schema_registry.sequences (entity_class, current_value)
                VALUES (:entity_class, 1) ON CONFLICT DO NOTHING
            """), {"entity_class": entity_class})
            return f"{entity_class}-1"
        return f"{entity_class}-{row.current_value}"

    # ========== BIRTH (ID 계승 및 UPSERT 보장) ==========

    async def birth_monewment(self, payload: dict) -> dict:
        target_id = payload.get("monewment_id") or payload.get("entity_id")
        # [MANDATE] gen_random_uuid() 제거, target_id 무조건 사용 (없으면 에러)
        if not target_id: raise ValueError("monewment_id is mandatory for birth")

        now_kst = datetime.now(KST).replace(tzinfo=None)
        q = text("""
            INSERT INTO schema_registry.monewments
                (monewment_id, display_name, owner_user_id, host_machine_id, core_version, status, born_at, last_seen_at)
            VALUES (:eid, :display_name, :owner_user_id, :host_machine_id, :core_version, 'ACTIVE', :now, :now)
            ON CONFLICT (monewment_id) DO UPDATE SET last_seen_at = :now, status = 'ACTIVE'
            RETURNING monewment_id, born_at
        """)
        res = await self.db.execute(q, {
            "eid": str(target_id),
            "display_name": payload["display_name"],
            "owner_user_id": payload["owner_user_id"],
            "host_machine_id": payload.get("host_machine_id"),
            "core_version": payload.get("core_version"),
            "now": now_kst
        })
        row = res.fetchone()
        return {"entity_id": str(row.monewment_id), "born_at": str(row.born_at), "fencing_token": 1}

    async def birth_stratum(self, payload: dict) -> dict:
        target_id = payload.get("stratum_id") or payload.get("entity_id")
        if not target_id: raise ValueError("stratum_id is mandatory for birth")

        # [MANDATE] 하이픈 치환 (PHYSICS-1 -> physics_1)
        stratum_name = payload["stratum_name"].replace("-", "_").lower()

        now_kst = datetime.now(KST).replace(tzinfo=None)
        q = text("""
            INSERT INTO schema_registry.stratums
                (stratum_id, stratum_name, monewment_id, purpose, schema_pg, status, born_at, last_seen_at)
            VALUES (:eid, :stratum_name, :monewment_id, :purpose, :schema_pg, 'ACTIVE', :now, :now)
            ON CONFLICT (stratum_id) DO UPDATE SET last_seen_at = :now, status = 'ACTIVE', stratum_name = :stratum_name
            RETURNING stratum_id, born_at
        """)
        res = await self.db.execute(q, {
            "eid": str(target_id),
            "stratum_name": stratum_name,
            "monewment_id": payload["monewment_id"],
            "purpose": payload.get("purpose"),
            "schema_pg": payload.get("schema_pg"),
            "now": now_kst
        })
        row = res.fetchone()
        return {"entity_id": str(row.stratum_id), "born_at": str(row.born_at), "fencing_token": 1}

    async def birth_queen(self, payload: dict) -> dict:
        target_id = payload.get("queen_id") or payload.get("entity_id")
        if not target_id: raise ValueError("queen_id is mandatory for birth")

        rel_type = payload.get("relationship_type", "INTERNAL").upper()
        entity_class = "QUEEN-IN" if rel_type == "INTERNAL" else "QUEEN-ALLY"
        official_name = await self._get_next_sequence(entity_class)
        
        now_kst = datetime.now(KST).replace(tzinfo=None)
        q = text("""
            INSERT INTO schema_registry.queens
                (queen_id, queen_name, relationship_type, queen_type, host_ip, api_key_masked, stratum_ids, status, born_at, last_seen_at)
            VALUES (:eid, :queen_name, :relationship_type, :queen_type, :host_ip, :api_key_masked, :stratum_ids, 'ACTIVE', :now, :now)
            ON CONFLICT (queen_id) DO UPDATE SET last_seen_at = :now, status = 'ACTIVE'
            RETURNING queen_id, born_at
        """)
        res = await self.db.execute(q, {
            "eid": str(target_id),
            "queen_name": official_name,
            "relationship_type": rel_type,
            "queen_type": payload.get("queen_type", "GENERAL"),
            "host_ip": payload.get("host_ip"),
            "api_key_masked": payload.get("api_key_masked"),
            "stratum_ids": payload.get("stratum_ids", []),
            "now": now_kst
        })
        row = res.fetchone()
        return {"entity_id": str(row.queen_id), "born_at": str(row.born_at), "official_name": official_name, "fencing_token": 1}

    async def birth_ant(self, payload: dict) -> dict:
        target_id = payload.get("ant_id") or payload.get("entity_id")
        if not target_id: raise ValueError("ant_id is mandatory for birth")

        ant_type = payload.get("ant_type", "CODE").upper()
        entity_class = f"ANT-{ant_type}"
        official_name = await self._get_next_sequence(entity_class)
        
        now_kst = datetime.now(KST).replace(tzinfo=None)
        q = text("""
            INSERT INTO schema_registry.ants
                (ant_id, ant_name, queen_id, stratum_id, ant_type, target_url, status, born_at, last_seen_at)
            VALUES (:eid, :ant_name, :queen_id, :stratum_id, :ant_type, :target_url, 'ACTIVE', :now, :now)
            ON CONFLICT (ant_id) DO UPDATE SET last_seen_at = :now, status = 'ACTIVE'
            RETURNING ant_id, born_at
        """)
        res = await self.db.execute(q, {
            "eid": str(target_id),
            "ant_name": official_name,
            "queen_id": payload["queen_id"],
            "stratum_id": payload["stratum_id"],
            "ant_type": ant_type,
            "target_url": payload.get("target_url"),
            "now": now_kst
        })
        row = res.fetchone()
        return {"entity_id": str(row.ant_id), "born_at": str(row.born_at), "official_name": official_name, "fencing_token": 1}

    async def birth_areum(self, payload: dict) -> dict:
        target_id = payload.get("areum_id") or payload.get("entity_id")
        if not target_id: raise ValueError("areum_id is mandatory for birth")

        is_ally = payload.get("is_ally", False)
        entity_class = "AREUM-ALLY" if is_ally else "AREUM-IN"
        official_name = await self._get_next_sequence(entity_class)
        
        now_kst = datetime.now(KST).replace(tzinfo=None)
        try:
            q1 = text("""
                INSERT INTO schema_registry.areums
                    (areum_id, areum_name, stratum_id, queen_id, ollama_model, status, born_at, last_seen_at)
                VALUES (:eid, :areum_name, :stratum_id, :queen_id, :ollama_model, 'ACTIVE', :now, :now)
                ON CONFLICT (areum_id) DO UPDATE SET last_seen_at = :now, status = 'ACTIVE'
                RETURNING areum_id, born_at
            """)
            res = await self.db.execute(q1, {
                "eid": str(target_id),
                "areum_name": official_name,
                "stratum_id": payload["stratum_id"],
                "queen_id": payload["queen_id"],
                "ollama_model": payload.get("ollama_model", "gemma3:4b"),
                "now": now_kst
            })
            row = res.fetchone()
            official_id = str(row[0])

            q2 = text("""
                INSERT INTO schema_pipeline.areum_registry
                    (areum_id, areum_name, stratum_id, queen_id, ollama_model, status, born_at, last_seen_at)
                VALUES (:eid, :areum_name, :stratum_id, :queen_id, :ollama_model, 'ACTIVE', :born, :now)
                ON CONFLICT (areum_id) DO UPDATE SET last_seen_at = :now, status = 'ACTIVE'
            """)
            await self.db.execute(q2, {
                "eid": official_id,
                "areum_name": official_name,
                "stratum_id": payload["stratum_id"],
                "queen_id": payload["queen_id"],
                "ollama_model": payload.get("ollama_model", "gemma3:4b"),
                "born": row[1],
                "now": now_kst
            })
            
            logger.info(f"[REGISTRY] Authoritative Identity UPSERT SUCCESS for AREUM {official_id}")
            return {"entity_id": official_id, "born_at": row[1].isoformat(), "official_name": official_name, "fencing_token": 1}
        except Exception as e:
            logger.error(f"[REGISTRY] Authoritative Birth FAILED: {e}")
            raise 

    # ========== PING & DEATH ==========

    async def ping(self, entity_type: str, entity_id: str) -> None:
        etype = entity_type.lower()
        if etype == "monewment": table = "schema_registry.monewments"
        elif etype == "stratum": table = "schema_registry.stratums"
        elif etype == "queen": table = "schema_registry.queens"
        elif etype == "areum": table = "schema_registry.areums"
        else: table = "schema_registry.ants" # areum/physics defaults
        
        id_col = f"{etype}_id" if etype in ["monewment", "stratum", "queen", "areum"] else "ant_id"
        
        now_kst = datetime.now(KST)
        await self.db.execute(text(f"UPDATE {table} SET last_seen_at = :now, status = 'ACTIVE' WHERE {id_col}::text = :eid"), {"eid": str(entity_id), "now": now_kst})

    async def death(self, entity_type: str, entity_id: str) -> None:
        etype = entity_type.lower()
        if etype == "monewment": table = "schema_registry.monewments"
        elif etype == "stratum": table = "schema_registry.stratums"
        elif etype == "queen": table = "schema_registry.queens"
        elif etype == "areum": table = "schema_registry.areums"
        else: table = "schema_registry.ants"
        
        id_col = f"{etype}_id" if etype in ["monewment", "stratum", "queen", "areum"] else "ant_id"
        
        now_kst = datetime.now(KST)
        await self.db.execute(text(f"UPDATE {table} SET status = 'DEAD', died_at = :now WHERE {id_col}::text = :eid"), {"eid": str(entity_id), "now": now_kst})

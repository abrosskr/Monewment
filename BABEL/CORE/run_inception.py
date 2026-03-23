import asyncio, json, httpx, sys, os
from datetime import datetime
from sqlalchemy import text

BABEL_PATH = r"C:\monewment\BABEL\CORE"
STRATUM_PATH = r"C:\monewment\STRATUM\STRATUM-1"
sys.path.append(BABEL_PATH)
sys.path.append(STRATUM_PATH)

from core.database import engine
from main import normalize_tag, conf
from knowledge_manager import SovereignKnowledge

# [V9.0 SOVEREIGN MAP] Local knowledge source
KNOWLEDGE = SovereignKnowledge.export_knowledge()
BABEL_MAP = {k: k for k in KNOWLEDGE['constants'].keys()}
BABEL_MAP.update({
    "beef": "BBL.ING.BEEF", "bacon": "BBL.ING.BACON", "chicken": "BBL.ING.CHICKEN",
    # ... 
})

UNMAPPED_LOG = os.path.join(BABEL_PATH, "unmapped_tags.log")

async def run_unified_inception():
    async with engine.connect() as conn:
        # 1. BABEL 소유 개념 선행 등록 (Seeding missing concepts)
        concepts_to_seed = []
        for b_id, meta in KNOWLEDGE['concepts'].items():
            concepts_to_seed.append({
                "babel_id": b_id,
                "canonical_name": meta['name'],
                "category": meta['cat'],
                "description": "Seeded via Sovereign Inception"
            })
        
        # [NEW] Constants as Concepts
        for b_id, meta in KNOWLEDGE['constants'].items():
            concepts_to_seed.append({
                "babel_id": b_id,
                "canonical_name": b_id.split('.')[-1].replace('_', ' ').capitalize(),
                "category": b_id.split('.')[1],
                "description": f"Physical Constant: {meta}"
            })

        # [NEW] Manual Mappings as Concepts
        for k, v in BABEL_MAP.items():
            if v not in [c['babel_id'] for c in concepts_to_seed]:
                concepts_to_seed.append({
                    "babel_id": v,
                    "canonical_name": v.split('.')[-1].replace('_', ' ').capitalize(),
                    "category": v.split('.')[1] if '.' in v else "MISC",
                    "description": "Auto-seeded via BABEL_MAP"
                })

        async with httpx.AsyncClient(timeout=None) as client:
            headers = {"X-Queen-Token": conf.GATEWAY_TOKEN}
            # ontology registration
            await client.post(f"{conf.CORE_URL}/pipeline/knowledge/concepts", json=concepts_to_seed, headers=headers)
            print(f"[V9.2] Seeded {len(concepts_to_seed)} concepts to core.")

            # 2. AREUM_DONE 자산 전수 조사
            res = await conn.execute(text('SELECT id, essence_tags, ai_confidence FROM "schema_stratum_STRATUM-1".assets WHERE pipeline_state = \'AREUM_DONE\''))
            assets = res.fetchall()
            
            for asset in assets:
                tags = asset.essence_tags if isinstance(asset.essence_tags, list) else json.loads(asset.essence_tags or "[]")
                triples = []
                for raw_tag in tags:
                    norm_tag = normalize_tag(raw_tag)
                    if norm_tag in BABEL_MAP:
                        triples.append({
                            "subject_id": BABEL_MAP[norm_tag],
                            "predicate": "BBL.REL.REFERENCED_IN",
                            "object_id": f"ASSET_{str(asset.id)[-8:]}",
                            "confidence_score": asset.ai_confidence or 1.0,
                            "source_queen_id": conf.QUEEN_ID # [BLOODLINE] QUEEN-ID 주입
                        })
                
                if triples:
                    # [V7.0] BBL 명명 규칙 준수 여부 증명 (Logging to unmapped_tags.log)
                    if not norm_tag.startswith("bbl."):
                        with open(UNMAPPED_LOG, "a", encoding="utf-8") as f:
                            f.write(f"[{datetime.now().isoformat()}] ID_VIOLATION: {norm_tag} does not follow BBL convention.\n")
                    
                    await client.post(f"{conf.CORE_URL}/pipeline/knowledge/inscribe", json=triples, headers=headers)

    print("[SUCCESS] V9.2 Sovereign Inception loop complete.")

if __name__ == "__main__":
    asyncio.run(run_unified_inception())

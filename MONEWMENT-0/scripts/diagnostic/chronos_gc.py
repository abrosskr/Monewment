"""
scripts/diagnostic/chronos_gc.py — Layer 3: CHRONOS-ANT Garbage Collector
Zero-Entropy Defense System — 주기적 자동 소각 스크립트

임무:
  [1] Zombie DB 소각    — ACTIVE이나 30분 이상 ping 없는 엔티티 → DEAD 처리
  [2] Partial-Spawn GC  — identity.vow/.env 없는 빈 폴더 → 72시간 유예 후 삭제
  [3] pending 파일 처리  — pending_death.json 재전송 후 삭제

사용법:
  python chronos_gc.py              # 실제 실행
  python chronos_gc.py --dry-run    # 시뮬레이션만 (아무것도 변경 안 함)

설계 원칙 (Non-Blocking, Fail-Safe):
  - asyncio.Semaphore(5) 로 DB 부하 최소화
  - 실패해도 다음 GC 사이클에 재시도 (강제 종료 없음)
  - --dry-run 모드로 언제든 부작용 없이 프리뷰 가능
  - 삭제 전 72시간 유예 — 즉시 삭제 없음 (헌법 제14장)
"""
import asyncio
import sys
import os
import json
import urllib.request
import logging
import io
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ─── UTF-8 로깅 (Win32 안전) ────────────────────────────────────────────────
_utf8_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    stream=_utf8_stream,
)
logger = logging.getLogger("chronos_gc")

# ─── Path 설정 ───────────────────────────────────────────────────────────────
root = Path(os.getcwd())
sys.path.insert(0, str(root / "MONEWMENT-0"))

env_path = root / "MONEWMENT-0" / ".env"
_settings: dict[str, str] = {}
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                _settings[k.strip()] = v.strip().strip('"').strip("'")
                os.environ[k.strip()] = _settings[k.strip()]

GATEWAY_TOKEN  = _settings.get("GATEWAY_TOKEN", "")
LOCAL_GOV_TOKEN = _settings.get("LOCAL_GOV_TOKEN", "mon_local_gov_token_default")
CORE_BASE = "http://127.0.0.1:8800/v1/registry"

try:
    from core.database import engine
    from sqlalchemy import text
except ImportError as e:
    logger.error(f"Import Error: {e}")
    sys.exit(1)

# ─── 상수 ────────────────────────────────────────────────────────────────────
ZOMBIE_THRESHOLD_MINUTES = 30      # ACTIVE + ping 없는 간격 (분)
PARTIAL_SPAWN_GRACE_HOURS = 72     # 파일 없는 폴더 삭제 유예 시간
ENTITY_DIRS = {
    "QUEEN":  [root / "QUEEN" / "QUEEN_LIST"],
    "AREUM":  [root / "AREUM"],
}
ENTITY_REQUIRED_FILES = {
    "QUEEN":  [".env"],
    "AREUM":  [".env"],
}
DB_LOCK = asyncio.Semaphore(5)     # DB 부하 최소화


# ─── GC 함수들 ────────────────────────────────────────────────────────────────

async def gc_zombie_db(dry_run: bool) -> int:
    """
    ACTIVE 상태이나 ZOMBIE_THRESHOLD_MINUTES 이상 ping이 없는 엔티티를 DEAD 처리.
    """
    logger.info("[GC-1] Zombie DB 소각 시작...")
    entity_tables = [
        ("schema_registry.ants",   "ant_id",   "ant_name"),
        ("schema_registry.queens", "queen_id", "queen_name"),
        ("schema_registry.areums", "areum_id", "areum_name"),
    ]
    killed = 0

    async with engine.connect() as conn:
        for table, id_col, name_col in entity_tables:
            try:
                async with DB_LOCK:
                    r = await conn.execute(text(f"""
                        SELECT {id_col}, {name_col}, last_seen_at
                        FROM {table}
                        WHERE status = 'ACTIVE'
                          AND last_seen_at < NOW() - INTERVAL '{ZOMBIE_THRESHOLD_MINUTES} minutes'
                    """))
                    zombies = r.fetchall()
            except Exception as e:
                logger.warning(f"[GC-1] {table} 조회 실패 (스킵): {e}")
                continue

            for z in zombies:
                entity_id, entity_name, last_seen = str(z[0]), z[1], z[2]
                elapsed_min = (datetime.now(timezone.utc) - last_seen).total_seconds() / 60
                entity_type = table.split(".")[-1].rstrip("s")  # ants → ant

                if dry_run:
                    logger.info(f"  [DRY-RUN] 소각 예정: {entity_name} ({elapsed_min:.0f}분 무응답)")
                else:
                    # Death API 호출
                    url = f"{CORE_BASE}/death/{entity_type}/{entity_id}"
                    body = json.dumps({"reason": "ZOMBIE_GC_CHRONOS"}).encode()
                    headers = {
                        "Content-Type": "application/json",
                        "X-Queen-Token": GATEWAY_TOKEN,
                        "X-Local-Gov-Token": LOCAL_GOV_TOKEN,
                    }
                    try:
                        req = urllib.request.Request(url, data=body, headers=headers, method="DELETE")
                        urllib.request.urlopen(req, timeout=5)
                        logger.info(f"  [GC-1] DEAD: {entity_name} ({elapsed_min:.0f}분 무응답)")
                        killed += 1
                    except Exception as e:
                        logger.error(f"  [GC-1] 소각 실패 {entity_name}: {e}")

    logger.info(f"[GC-1] 완료 — {'(dry-run) ' if dry_run else ''}Zombie {killed}개 처리")
    return killed


def gc_partial_spawn_dirs(dry_run: bool) -> int:
    """
    72시간 이상 경과한 빈 엔티티 폴더(Partial-Spawn) 삭제.
    헌법 제14장: 즉시 삭제 없음 — 72시간 유예 보장.
    """
    import shutil
    logger.info(f"[GC-2] Partial-Spawn 폴더 GC 시작 (유예: {PARTIAL_SPAWN_GRACE_HOURS}h)...")
    removed = 0
    now = datetime.now().timestamp()

    for entity_type, base_paths in ENTITY_DIRS.items():
        required = ENTITY_REQUIRED_FILES.get(entity_type, [])
        for base_path in base_paths:
            if not base_path.exists():
                continue
            for candidate in base_path.rglob("*"):
                if not candidate.is_dir():
                    continue
                depth = len(candidate.relative_to(base_path).parts)
                if depth > 3:
                    continue
                name = candidate.name
                if not any(name.startswith(p) for p in ["QUEEN-", "AREUM-", "ANT-"]):
                    continue

                # 유예 기간 체크
                age_hours = (now - candidate.stat().st_mtime) / 3600
                if age_hours < PARTIAL_SPAWN_GRACE_HOURS:
                    continue

                children = list(candidate.iterdir())
                child_names = {c.name for c in children}
                missing = [f for f in required if f not in child_names]
                is_empty = len(children) == 0

                if is_empty or missing:
                    if dry_run:
                        reason = "비어있음" if is_empty else f"누락: {missing}"
                        logger.info(f"  [DRY-RUN] 삭제 예정: {candidate} ({age_hours:.0f}h, {reason})")
                    else:
                        try:
                            shutil.rmtree(candidate)
                            reason = "비어있음" if is_empty else f"누락: {missing}"
                            logger.info(f"  [GC-2] 삭제: {candidate} ({age_hours:.0f}h, {reason})")
                            removed += 1
                        except Exception as e:
                            logger.error(f"  [GC-2] 삭제 실패 {candidate}: {e}")

    logger.info(f"[GC-2] 완료 — {'(dry-run) ' if dry_run else ''}Partial-Spawn {removed}개 처리")
    return removed


def gc_pending_files(dry_run: bool) -> int:
    """
    pending_death.json 재전송 처리.
    전송 성공 시 파일 삭제, 실패 시 보존.
    """
    logger.info("[GC-3] pending_death.json 처리 시작...")
    pending_death = root / "pending_death.json"
    processed = 0

    if pending_death.exists():
        try:
            with open(pending_death, "r", encoding="utf-8") as f:
                records = json.load(f)
            if not isinstance(records, list):
                records = [records]

            failed = []
            for rec in records:
                ant_id = rec.get("ant_id") or rec.get("entity_id")
                entity_type = rec.get("entity_type", "ant")
                if not ant_id:
                    continue
                if dry_run:
                    logger.info(f"  [DRY-RUN] pending death 재전송 예정: {ant_id}")
                    continue
                url = f"{CORE_BASE}/death/{entity_type}/{ant_id}"
                body = json.dumps({"reason": "PENDING_RETRY_CHRONOS"}).encode()
                headers = {
                    "Content-Type": "application/json",
                    "X-Queen-Token": GATEWAY_TOKEN,
                    "X-Local-Gov-Token": LOCAL_GOV_TOKEN,
                }
                try:
                    req = urllib.request.Request(url, data=body, headers=headers, method="DELETE")
                    urllib.request.urlopen(req, timeout=5)
                    logger.info(f"  [GC-3] pending death 처리: {ant_id}")
                    processed += 1
                except Exception as e:
                    logger.warning(f"  [GC-3] 재전송 실패 (보존): {ant_id}: {e}")
                    failed.append(rec)

            if not dry_run:
                if failed:
                    with open(pending_death, "w", encoding="utf-8") as f:
                        json.dump(failed, f, ensure_ascii=False)
                    logger.info(f"  [GC-3] {len(failed)}개 미처리 항목 보존")
                else:
                    pending_death.unlink()
                    logger.info("  [GC-3] pending_death.json 완전 처리 후 삭제")
        except Exception as e:
            logger.error(f"  [GC-3] pending_death.json 처리 오류: {e}")
    else:
        logger.info("  [GC-3] pending_death.json 없음 - 정상")

    return processed


# ─── 메인 ────────────────────────────────────────────────────────────────────

async def main():
    dry_run = "--dry-run" in sys.argv

    mode_label = "[DRY-RUN MODE]" if dry_run else "[LIVE MODE]"
    logger.info("=" * 60)
    logger.info(f"  CHRONOS-ANT GC v1.0 {mode_label}")
    logger.info(f"  Zombie threshold: {ZOMBIE_THRESHOLD_MINUTES}min")
    logger.info(f"  Partial-Spawn grace: {PARTIAL_SPAWN_GRACE_HOURS}h")
    logger.info("=" * 60)

    # GC-1: Zombie DB
    zombie_count = await gc_zombie_db(dry_run)

    # GC-2: Partial-Spawn dirs
    partial_count = gc_partial_spawn_dirs(dry_run)

    # GC-3: pending files
    pending_count = gc_pending_files(dry_run)

    total = zombie_count + partial_count + pending_count
    logger.info("=" * 60)
    logger.info(f"  [CHRONOS REPORT] Zombie={zombie_count} | Partial={partial_count} | Pending={pending_count} | Total={total}")
    if total == 0:
        logger.info("  [OK] 제국 청결 상태 확인됨 - 소각 대상 없음")
    else:
        logger.info(f"  [DONE] {total}개 항목 처리 완료")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

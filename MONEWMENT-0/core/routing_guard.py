"""
core/routing_guard.py
[INTEGRITY PROTOCOL] 라우팅 무결성 보증 모듈
모든 워커와 레포지토리는 이 모듈을 통해 stratum_name, 경로, 해시를 검증해야 합니다.
"""
import re
import hashlib
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


# ─── R1: stratum_name SQL 인젝션 방지 ───────────────────────────────────────
_SAFE_STRATUM = re.compile(r'^[a-z0-9_]{1,50}$')

def validate_stratum_name(name: str) -> str:
    """
    stratum_name 이 안전한 식별자인지 검증합니다.
    위반 시 ValueError 를 발생시켜 워커 진입을 즉시 차단합니다.
    """
    if not isinstance(name, str) or not _SAFE_STRATUM.match(name):
        raise ValueError(
            f"[ROUTING GUARD R1] Invalid stratum_name: {name!r}. "
            f"Only lowercase alphanumeric and underscores (1-50 chars) allowed."
        )
    return name


# ─── R2: QUEEN 권한 검증 ─────────────────────────────────────────────────────
async def verify_queen_authorization(queen_id: str, stratum_name: str, db: AsyncSession) -> None:
    """
    QUEEN 이 해당 STRATUM 을 처리할 권한이 registry 에 등록되어 있는지 확인합니다.
    미인가 시 PermissionError 를 발생시켜 외부 AI 데이터 유출을 차단합니다.
    """
    result = await db.execute(text("""
        SELECT 1 FROM schema_registry.queens
        WHERE queen_id = :qid
          AND :sname = ANY(stratum_ids::text[])
          AND status != 'DEAD'
    """), {"qid": queen_id, "sname": stratum_name})

    if not result.fetchone():
        raise PermissionError(
            f"[ROUTING GUARD R2] QUEEN '{queen_id}' is NOT authorized for stratum '{stratum_name}'. "
            f"Update schema_registry.queens.stratum_ids to grant access."
        )


# ─── R3: stratum_id vs 스키마 일치 검증 ─────────────────────────────────────
def validate_stratum_id_match(stratum_id: str, schema: str) -> None:
    """
    pipeline_tasks 에 삽입할 stratum_id 가 실제 스키마의 suffix 와 일치하는지 확인합니다.
    불일치 시 ValueError 를 발생시켜 교차오염을 차단합니다.
    """
    expected = schema.removeprefix("schema_stratum_")
    if stratum_id != expected:
        raise ValueError(
            f"[ROUTING GUARD R3] stratum_id mismatch: "
            f"got='{stratum_id}', expected='{expected}' (from schema='{schema}'). "
            f"Data cross-contamination prevented."
        )


# ─── R4a: payload_locator 경로 화이트리스트 검증 ──────────────────────────────
def validate_payload_path(path_str: str, storage_root: str, allowed_zones: list[str]) -> Path:
    """
    payload_locator 가 허용된 스토리지 존 내에 있는지 확인합니다.
    경로 탈출(Path Traversal) 및 위변조된 경로를 차단합니다.
    """
    resolved = Path(path_str).resolve()
    root = Path(storage_root).resolve()

    allowed = any(
        resolved.is_relative_to(root / zone)
        for zone in allowed_zones
    )

    if not allowed:
        raise ValueError(
            f"[ROUTING GUARD R4a] Path not in allowed zones: {resolved}. "
            f"Allowed: {[str(root / z) for z in allowed_zones]}"
        )
    return resolved


# ─── R4b: SHA-256 해시 무결성 검증 ───────────────────────────────────────────
def verify_payload_hash(path: Path, expected_hash: str | None) -> str:
    """
    파일의 실제 SHA-256 해시를 계산하고 DB 에 기록된 해시와 대조합니다.
    불일치 시 ValueError 를 발생시켜 위변조된 파일이 AI 로 전달되는 것을 차단합니다.
    expected_hash 가 None 이면 검증을 건너뜁니다 (기존 레거시 레코드 호환).
    """
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected_hash and actual != expected_hash:
        raise ValueError(
            f"[ROUTING GUARD R4b] Hash mismatch for {path.name}. "
            f"expected={expected_hash[:16]}... actual={actual[:16]}... "
            f"Possible forgery or file corruption."
        )
    return actual

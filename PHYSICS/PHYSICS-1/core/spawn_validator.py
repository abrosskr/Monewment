"""
core/spawn_validator.py — Layer 2: Spawn Integrity Validator
Zero-Entropy Defense System — 엔티티 탄생 직후 물리 인스턴스 완성 검증

사용법 (spawn_areum.py 등에서 import):
    from core.spawn_validator import validate_spawn_or_kill
    validate_spawn_or_kill(
        gateway_base="http://127.0.0.1:8800/v1/registry",
        entity_type="areum",
        entity_id=result["entity_id"],
        instance_path=Path("c:/monewment/AREUM-TEST"),
        expected_files=[".env", "worker_areum.py"],
        local_gov_token="mon_local_gov_token_default",
    )

설계 원칙 (Non-Blocking):
  - 검증 실패해도 스폰 흐름 차단 없음 (Fail-Safe)
  - 파일 존재 확인만 수행 (I/O 최소화)
  - 실패 시 DB만 DEAD 처리 + 경고 로그
"""
import logging
import urllib.request
import json
from pathlib import Path

logger = logging.getLogger("spawn_validator")


def _kill_entity_in_db(
    gateway_base: str,
    entity_type: str,
    entity_id: str,
    local_gov_token: str,
    gateway_token: str,
    reason: str = "PARTIAL_SPAWN_ENTROPY",
) -> bool:
    """DB에서 엔티티를 DEAD 처리한다. 실패해도 예외를 올리지 않는다."""
    url = f"{gateway_base}/death/{entity_type}/{entity_id}"
    body = json.dumps({"reason": reason}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Queen-Token": gateway_token,
        "X-Local-Gov-Token": local_gov_token,
    }
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method="DELETE")
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read())
            logger.warning(
                f"[SPAWN_VALIDATOR] Entity {entity_type}/{entity_id} killed: {result.get('status')}"
            )
            return True
    except Exception as e:
        logger.error(f"[SPAWN_VALIDATOR] DB kill failed for {entity_id}: {e}")
        return False


def validate_spawn_or_kill(
    gateway_base: str,
    entity_type: str,
    entity_id: str,
    instance_path: Path,
    expected_files: list[str],
    local_gov_token: str = "mon_local_gov_token_default",
    gateway_token: str = "",
) -> bool:
    """
    스폰 직후 물리 인스턴스 완성 여부를 검증한다.

    Returns:
        True  — 검증 성공 (정상)
        False — 검증 실패 (Partial-Spawn; DB kill 처리됨)
    """
    instance_path = Path(instance_path)

    # [1] 폴더 존재 확인
    if not instance_path.exists():
        logger.error(
            f"[SPAWN_VALIDATOR] PARTIAL_SPAWN: '{instance_path}' 폴더 없음. "
            f"entity={entity_type}/{entity_id}"
        )
        _kill_entity_in_db(
            gateway_base, entity_type, entity_id,
            local_gov_token, gateway_token, "PARTIAL_SPAWN_NO_DIR"
        )
        return False

    # [2] 필수 파일 존재 확인
    child_names = {c.name for c in instance_path.iterdir()}
    missing = [f for f in expected_files if f not in child_names]
    if missing:
        logger.error(
            f"[SPAWN_VALIDATOR] PARTIAL_SPAWN: '{instance_path}' 필수 파일 누락: {missing}. "
            f"entity={entity_type}/{entity_id}"
        )
        _kill_entity_in_db(
            gateway_base, entity_type, entity_id,
            local_gov_token, gateway_token, f"PARTIAL_SPAWN_MISSING:{','.join(missing)}"
        )
        return False

    logger.info(
        f"[SPAWN_VALIDATOR] OK: {entity_type}/{entity_id} @ {instance_path}"
    )
    return True

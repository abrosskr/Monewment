"""
core/registry.py
G2: Manifest reload on startup — 재시작 시 상태 복원 (메모리 캐시 + 파일 내구성)
G5: 레거시 typing 제거
G9: 하드코딩 경로 → 동적 해결
"""
import json
import logging
from pathlib import Path

logger = logging.getLogger("core.registry")

# [G9] 동적 경로 해결 — docs/ 폴더로 통합된 manifest 참조
_DEFAULT_MANIFEST = Path(__file__).resolve().parent.parent / "docs" / "structural_manifest.json"


class StratumRegistry:
    """
    In-memory stratum registry backed by structural_manifest.json.
    [G2] 재시작 시 manifest 로부터 alias 와 live_instances 를 복원합니다.
    """

    def __init__(self):
        self._strata: dict[str, dict] = {}
        self._aliases: dict[str, dict] = {}
        self.load_manifest()

    def load_manifest(self, manifest_path: Path | None = None) -> None:
        """
        [G2+G9] manifest_path 가 없으면 프로젝트 루트의 structural_manifest.json 을 사용.
        실패해도 빈 상태로 계속 동작 (경고 로그).
        """
        path = manifest_path or _DEFAULT_MANIFEST
        if not path.exists():
            logger.warning(f"[REGISTRY] Manifest not found at {path}. Starting with empty registry.")
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self._aliases = data.get("external_aliases", {})

            # [G2] live_instances 복원 — manifest 는 dict {id: {...}} 형태
            live_instances = data.get("live_instances", {})
            if isinstance(live_instances, dict):
                # structural_manifest.json 형식: {"ANT-USER-777": {...}, ...}
                for sid, inst in live_instances.items():
                    if isinstance(inst, dict):
                        self._strata[sid] = {
                            "name": inst.get("name", sid),
                            "status": inst.get("status", "ACTIVE"),
                            "type": inst.get("type", "RESTORED"),
                        }
            elif isinstance(live_instances, list):
                # 혹시 리스트 형식인 경우 (구버전 호환)
                for inst in live_instances:
                    if isinstance(inst, dict):
                        sid = inst.get("id") or inst.get("stratum_id")
                        if sid:
                            self._strata[sid] = {
                                "name": inst.get("name", sid),
                                "status": inst.get("status", "ACTIVE"),
                                "type": inst.get("type", "RESTORED"),
                            }

            logger.info(
                f"[REGISTRY] Loaded {len(self._aliases)} aliases, "
                f"{len(self._strata)} live instances from {path.name}."
            )
        except Exception as e:
            logger.error(f"[REGISTRY] Failed to load manifest: {e}")

    def register_stratum(self, stratum_id: str, config: dict) -> None:
        self._strata[stratum_id] = config
        logger.info(f"[REGISTRY] STRATUM Registered: {stratum_id}")

    def get_stratum_config(self, stratum_id: str) -> dict | None:
        return self._strata.get(stratum_id)

    def is_valid(self, stratum_id: str) -> bool:
        return stratum_id in self._strata

    def resolve_alias(self, alias: str) -> dict | None:
        return self._aliases.get(alias.upper())


registry = StratumRegistry()

# Legacy stratum registration (하드코딩 — manifest 복원 이후에도 항상 보장)
registry.register_stratum("STRATUM-1", {
    "name": "vendors_legacy",
    "queens": ["QUEEN-LEGACY-VENDORS"],
    "status": "ACTIVE",
})

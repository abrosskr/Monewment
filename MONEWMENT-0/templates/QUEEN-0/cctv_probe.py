"""
cctv_probe.py — CCTV Probe (Decentralized Context Synchronizer)
[G8] TECH_SPEC 위반 교정:
  - os.environ.get() → pydantic-settings 로 교체
  - print() → logging.getLogger 로 교체
  - 수동 .env 파싱 제거
[G6] 허용된 레벨만 전송 (클라이언트 측 화이트리스트)
"""
import logging
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("cctv_probe")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(name)s] %(levelname)s: %(message)s"))
    logger.addHandler(handler)


# [G8] pydantic-settings 로 환경 변수 관리
class ProbeSettings(BaseSettings):
    CCTV_SECRET: str
    CORE_HOST: str = "127.0.0.1"
    PORT_CORE_API: str = "8800"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# [G6] 클라이언트 측 레벨 화이트리스트
_ALLOWED_LEVELS = {"QUEEN", "ANT", "STRATUM", "MONEWMENT"}


def run_cctv_probe(level: str) -> None:
    """
    [Decentralized CCTV Probe]
    Fetches the live system documentation for the given level from the MONEWMENT Core
    and saves it as LIVE_CONTEXT.md and 06_API_REGISTRY.md.
    """
    level_upper = level.upper()

    # [G6] 레벨 검증
    if level_upper not in _ALLOWED_LEVELS:
        logger.error(f"[G6] Invalid level: {level!r}. Allowed: {sorted(_ALLOWED_LEVELS)}")
        sys.exit(1)

    logger.info(f"Synchronizing {level_upper} context from MONEWMENT Core...")

    try:
        probe_settings = ProbeSettings()
    except Exception as e:
        logger.error(f"[G8] Settings load failed — is CCTV_SECRET set in .env? Error: {e}")
        sys.exit(1)

    url = f"http://{probe_settings.CORE_HOST}:{probe_settings.PORT_CORE_API}/cctv/sync/{level_upper}"
    req = urllib.request.Request(url, headers={"X-CCTV-Secret": probe_settings.CCTV_SECRET})

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                markdown_content = data.get("markdown", "")

                target_dir = Path(f".{level_upper.lower()}")
                target_dir.mkdir(exist_ok=True)

                context_file = target_dir / "LIVE_CONTEXT.md"
                context_file.write_text(markdown_content, encoding="utf-8")
                logger.info(f"[OK] Live context synchronized: {context_file}")
            else:
                logger.warning(f"Core returned HTTP {response.status}. Using cached context.")
    except urllib.error.HTTPError as e:
        logger.warning(f"HTTP Error {e.code}: {e.reason}. Check CCTV_SECRET and level.")
    except Exception as e:
        logger.warning(f"Failed to reach Core ({e}). Continuing with existing cached documentation.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python cctv_probe.py {queen|ant|stratum|monewment}")
        sys.exit(1)
    run_cctv_probe(sys.argv[1])

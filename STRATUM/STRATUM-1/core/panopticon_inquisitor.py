import asyncio
import os
import json
import logging
from core.ast_extractor import find_route_file, extract_surrounding_context

logger = logging.getLogger("Inquisitor")

try:
    from core.database import redis_client
except ImportError:
    redis_client = None


class StratumInquisitor:
    """
    [Phase 2: Stratum Inquisitor (영토 내 격리 심문관)]
    MONEWMENT 헌법 제2장 '통제 침범 금지 원칙(Isolation)'을 준수하여,
    오직 자신이 속한 로컬 영토 내의 코드베이스(AST)만 분석하고 
    이벤트 메타 보고서를 REX 단으로 송신합니다.
    """
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.stream_name = "panopticon:incidents"
        self.consumer_group = "local_inquisitors"
        self.consumer_name = f"inq_{os.getpid()}"

    async def setup_stream(self):
        if not redis_client: return
        try:
            # Create consumer group if it doesn't exist
            await redis_client.xgroup_create(self.stream_name, self.consumer_group, mkstream=True)
        except Exception:
            pass # Already exists

    async def run(self):
        if not redis_client:
            logger.error("[INQUISITOR] Redis is not configured. Shutting down.")
            return

        await self.setup_stream()
        logger.info(f"[INQUISITOR] Booted. Monitoring local stratum codebase at {self.base_dir}")
        
        while True:
            try:
                # 10분 단위 애그리게이션 된 이벤트들을 큐에서 수신합니다.
                messages = await redis_client.xreadgroup(
                    self.consumer_group,
                    self.consumer_name,
                    {self.stream_name: ">"},
                    count=10,
                    block=5000
                )
                
                if not messages:
                    continue
                    
                for stream, msg_list in messages:
                    for msg_id, payload in msg_list:
                        await self.process_incident(msg_id, payload)
                        # 처리완료 응답 (서킷 블락된 다수의 메시지를 병합 처리)
                        await redis_client.xack(self.stream_name, self.consumer_group, msg_id)
                        
            except Exception as e:
                logger.error(f"[INQUISITOR] Error in worker loop: {e}")
                await asyncio.sleep(5)

    async def process_incident(self, msg_id, payload: dict):
        # Redis Stream payload 딕셔너리의 key/val은 bytes로 들어옵니다.
        def _decode(v): return v.decode('utf-8') if isinstance(v, bytes) else str(v)
        
        path = _decode(payload.get(b"path", "")) or _decode(payload.get("path", ""))
        status_code = _decode(payload.get(b"status_code", "")) or _decode(payload.get("status_code", ""))
        
        if not path:
            return
            
        logger.info(f"[INQUISITOR] Local incident acquired: Status {status_code} at {path}")
        
        # 1. AST 파싱: "어느 파일의 어느 함수에서 터졌는가?" -> 소스코드 추출
        # (로컬 영토 내 파일만 탐색, 격리 원칙 완벽 준수)
        # [EVENT LOOP PROTECTION] Offload heavy sync I/O and AST parsing to thread pool
        file_path, line_num = await asyncio.to_thread(find_route_file, self.base_dir, path)
        
        if file_path:
            snippet = await asyncio.to_thread(extract_surrounding_context, file_path, line_num)
            logger.info(f"[INQUISITOR] Surgical AST cut performed on {file_path}")
        else:
            snippet = "[코드 추출 병목] 지정된 라우터를 로컬 영토 내에서 스캔할 수 없습니다."
            
        # 2. 메타 보고서 작성 (LLM 호출 비용 방어를 위해 즉시 텍스트화 압축)
        meta_report = {
            "incident_id": _decode(msg_id),
            "stratum_base": self.base_dir,
            "path": path,
            "status_code": status_code,
            "local_code_snippet": snippet,
        }
        
        # 3. MONEWMENT-0 밖의 영역(`EDENVALE/REX`)으로 보고서 송출 (Push to Global Queue)
        await redis_client.xadd("panopticon:reports_for_rex", {"report": json.dumps(meta_report)})
        logger.info("[INQUISITOR] Local Meta Report assembled and dispatched to REX global layer.")


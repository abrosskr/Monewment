# MONEWMENT-0/core/logger.py
import sys
import logging
import re
from typing import TextIO

# [TECH SPEC] 마스킹 대상 키워드
MASK_KEYWORDS = ["password", "pwd", "secret", "token", "api_key", "key"]

class MaskedStream:
    """stdout/stderr를 가로채어 민감 정보를 마스킹하는 스트림 객체"""
    def __init__(self, original_stream: TextIO):
        self.original_stream = original_stream

    def write(self, data: str):
        if not data.strip():
            try:
                self.original_stream.write(data)
            except (UnicodeEncodeError, BlockingIOError):
                # Fallback for Windows consoles or temporary IO issues
                try:
                    encoding = getattr(self.original_stream, 'encoding', 'utf-8') or 'utf-8'
                    self.original_stream.write(data.encode(encoding, errors='replace').decode(encoding))
                except:
                    pass
            return

        masked_data = data
        # 1. URL 내 인증 정보 마스킹 (://user:password@)
        masked_data = re.sub(r'(://)([^:]+):([^@]+)(@)', r'\1\2:****\4', masked_data)
        
        # 2. Key-Value 구조 마스킹
        for kw in MASK_KEYWORDS:
            pattern = rf'("{kw}"\s*:\s*")([^"]+)(")'
            masked_data = re.sub(pattern, r'\1[MASKED]\3', masked_data, flags=re.IGNORECASE)
        
        try:
            self.original_stream.write(masked_data)
        except (UnicodeEncodeError, BlockingIOError):
            # Fallback for Windows consoles (cp949, etc.)
            try:
                encoding = getattr(self.original_stream, 'encoding', 'utf-8') or 'utf-8'
                # Attempt to write with replacement characters if the direct write fails
                safe_data = masked_data.encode(encoding, errors='replace').decode(encoding)
                self.original_stream.write(safe_data)
            except:
                # Last resort: just try to write it as is and ignore errors if possible
                pass

    def flush(self):
        try:
            self.original_stream.flush()
        except:
            pass

    def isatty(self):
        return self.original_stream.isatty()

    def __getattr__(self, name):
        return getattr(self.original_stream, name)

def setup_logger():
    # Windows 환경에서 UTF-8 지원을 위해 스트림 재설정 시도
    for stream_name in ['stdout', 'stderr']:
        stream = getattr(sys, stream_name)
        if hasattr(stream, 'reconfigure'):
            try:
                stream.reconfigure(encoding='utf-8')
            except:
                pass

    # sys.stdout/stderr 가로채기
    sys.stdout = MaskedStream(sys.stdout)
    sys.stderr = MaskedStream(sys.stderr)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout
    )
    return logging.getLogger("MONEWMENT")

logger = setup_logger()
import logging
import sys
import structlog
from typing import Any
from pathlib import Path
from logging.handlers import RotatingFileHandler
from src.config import settings

def mask_sensitive_data(logger, method_name, event_dict):
    """
    민감한 정보를 마스킹하는 프로세서
    """
    sensitive_keys = [
        'password', 'token', 'api_key', 'secret', 'authorization',
        'access_token', 'refresh_token', 'private_key', 'hashed_password'
    ]
    
    for key in list(event_dict.keys()):
        # 키 이름이 민감한 정보를 포함하는지 확인
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            event_dict[key] = '***MASKED***'
        
        # 값이 문자열이고 특정 패턴을 포함하는지 확인
        if isinstance(event_dict.get(key), str):
            value = event_dict[key]
            # JWT 토큰 패턴 감지 (eyJ로 시작)
            if value.startswith('eyJ') and len(value) > 20:
                event_dict[key] = f"{value[:10]}...***MASKED***"
    
    return event_dict

def setup_logger():
    """
    Configures structlog for JSON output (production-ready)
    with file rotation, sensitive data masking, and multiple handlers.
    """
    
    # [Phase 3] LOG_LEVEL을 환경 변수에서 로드
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # 로그 디렉토리 생성
    log_dir = settings.BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 핸들러 설정
    handlers = []
    
    # 1. 콘솔 핸들러 (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    handlers.append(console_handler)
    
    # 2. 일반 로그 파일 (로테이션)
    file_handler = RotatingFileHandler(
        log_dir / "monewment.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    handlers.append(file_handler)
    
    # 3. 에러 전용 로그 파일
    error_handler = RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    handlers.append(error_handler)
    
    # 4. 액세스 로그 파일 (INFO 이상)
    access_handler = RotatingFileHandler(
        log_dir / "access.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3,
        encoding='utf-8'
    )
    access_handler.setLevel(logging.INFO)
    handlers.append(access_handler)
    
    # Validation: Basic Config
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=handlers
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        mask_sensitive_data,  # 민감 정보 마스킹
    ]

    # JSON Renderer for Production
    processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Return a proxy that mimics standard logger but uses structlog
    return structlog.get_logger()

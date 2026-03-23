from contextvars import ContextVar
from typing import Optional

tenant_id: ContextVar[Optional[str]] = ContextVar("tenant_id", default=None)

def get_tenant_id() -> Optional[str]:
    return tenant_id.get()

def set_tenant_id(value: Optional[str]):
    tenant_id.set(value)
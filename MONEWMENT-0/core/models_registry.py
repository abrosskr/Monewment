"""
core/models_registry.py — API Contract v2.0
Added: idempotency_key, fencing_token, predecessor_id, death_reason, instance_path
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# --- Enums as literals ---
EntityStatus    = str  # 'ACTIVE' | 'DORMANT' | 'DEAD'
RelationshipType = str # 'INTERNAL' | 'ALLY'
QueenType       = str  # 'CRAWLER' | 'REX' | 'CLOUD_AI' | 'GENERAL'
AntType         = str  # 'CRAWLER' | 'PARSER' | 'FORAGER'
DeathReason     = str  # 'TASK_COMPLETE' | 'ERROR' | 'KILLED' | 'TIMEOUT' | 'COST_CAP'


class MonewmentEntity(BaseModel):
    monewment_id: str
    display_name: str
    owner_user_id: str
    host_machine_id: str | None = None
    core_version: str | None = None
    status: EntityStatus = 'ACTIVE'
    total_stratum_count: int = 0
    uptime_seconds: int = 0
    fencing_token: int = 1
    predecessor_id: str | None = None
    born_at: datetime
    last_seen_at: datetime
    died_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class StratumEntity(BaseModel):
    stratum_id: str
    stratum_name: str
    monewment_id: str | None = None
    purpose: str | None = None
    schema_pg: str | None = None
    root_path: str | None = None
    cloud_ai_enabled: bool = False
    total_cost_cents: float = 0.0
    budget_limit: float = 1000000000.0     # [V51.5]
    queen_count: int = 0
    status: EntityStatus = 'ACTIVE'
    fencing_token: int = 1
    predecessor_id: str | None = None
    born_at: datetime
    last_seen_at: datetime
    died_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class QueenEntity(BaseModel):
    queen_id: str
    queen_name: str
    stratum_ids: list[str] = []
    relationship_type: RelationshipType = 'INTERNAL'
    queen_type: QueenType = 'GENERAL'
    api_key_masked: str | None = None
    active_ant_count: int = 0
    total_tasks_completed: int = 0
    host_ip: str | None = None
    status: EntityStatus = 'ACTIVE'
    fencing_token: int = 1
    predecessor_id: str | None = None
    born_at: datetime
    last_seen_at: datetime
    died_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class AntEntity(BaseModel):
    ant_id: str
    ant_name: str
    queen_id: str | None = None
    stratum_id: str | None = None
    ant_type: AntType = 'CODE'
    task_id: str | None = None
    target_url: str | None = None
    payload_hash: str | None = None
    items_collected: int = 0
    error_message: str | None = None
    status: str = 'RUNNING'
    fencing_token: int = 1
    predecessor_id: str | None = None
    total_cost_cents: float = 0.0
    born_at: datetime
    last_seen_at: datetime
    died_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class AreumEntity(BaseModel):
    areum_id: str
    areum_name: str
    stratum_id: str
    queen_id: str | None = None
    ollama_model: str = 'gemma3:4b'
    status: EntityStatus = 'ACTIVE'
    fencing_token: int = 1
    predecessor_id: str | None = None
    born_at: datetime
    last_seen_at: datetime
    died_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


# --- Request models (v2.0) ---
class BirthRequest(BaseModel):
    entity_type: str          # 'monewment' | 'stratum' | 'queen' | 'ant' | 'areum'
    payload: dict
    instance_path: str | None = None  # Birth Sacrament — doc 이식 경로

class PingRequest(BaseModel):
    note: str | None = None   # 현재 작업 자유 메모
    current_session_cost: float = 0.0 # [V51.5] Governance tracking
    payload: dict | None = None

class DeathRequest(BaseModel):
    reason: DeathReason | None = "TASK_COMPLETE"
    final_cost_cents: float = 0.0

class MaterializeRequest(BaseModel):
    entity_type: str
    instance_path: str

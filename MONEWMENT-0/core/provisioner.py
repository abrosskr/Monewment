from sqlalchemy import text
from .database import engine
from .logger import logger
from .audit_logger import AuditLogger

class Provisioner:
    """물리적 영토(Stratum)의 DB 스키마와 기본 테이블을 생성하는 코어 모듈"""
    @staticmethod
    async def create_stratum_space(stratum_name: str):
        schema_name = f"schema_stratum_{stratum_name}"
        logger.info(f"[PROVISIONER] Creating Stratum space: {schema_name}")
        async with engine.begin() as conn:
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name};"))
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.vendors (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) UNIQUE NOT NULL,
                    base_url VARCHAR(255) NOT NULL,
                    crawl_interval INT DEFAULT 3600,
                    status VARCHAR(50) DEFAULT 'ACTIVE',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.crawl_logs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    vendor_id UUID REFERENCES {schema_name}.vendors(id) ON DELETE CASCADE,
                    status VARCHAR(50) NOT NULL,
                    items_count INT DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.assets (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    vendor_id UUID REFERENCES {schema_name}.vendors(id) ON DELETE CASCADE,
                    raw_data JSONB, -- [HYBRID] storage_path가 있으면 NULL 가능
                    storage_path VARCHAR(512), -- [DECREE 12.1] Supabase Storage reference
                    hash VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    -- [AREUM] QUEEN-AREUM 공동 소유 칼럼 (AREUM이 분석 완료 후 채움)
                    ai_summary TEXT,
                    essence_tags JSONB DEFAULT '[]'::jsonb,
                    ai_confidence FLOAT,
                    areum_id UUID,
                    areum_processed_at TIMESTAMP WITH TIME ZONE,
                    rex_summary TEXT, -- [V51.5] REX Synthesis Result
                    rex_processed_at TIMESTAMP WITH TIME ZONE, -- [V51.5] REX Synthesis Timestamp
                    pipeline_state VARCHAR(50) DEFAULT 'RAW_DUMPED',
                    accumulated_cost FLOAT DEFAULT 0.0 -- [V51.5]
                );
            """))

            # [Auto-Ignition] Trigger function to NOTIFY Sentinel with full context
            await conn.execute(text(f"""
                CREATE OR REPLACE FUNCTION {schema_name}.notify_new_asset()
                RETURNS trigger AS $$
                DECLARE
                    s_id uuid;
                    q_id uuid;
                BEGIN
                    -- Resolve Stratum ID and its primary Queen ID for spawning
                    SELECT stratum_id INTO s_id FROM schema_registry.stratums WHERE stratum_name = '{stratum_name}' LIMIT 1;
                    SELECT queen_id INTO q_id FROM schema_registry.queens WHERE s_id = ANY(stratum_ids) LIMIT 1;
                    
                    PERFORM pg_notify('stratum_asset_inserted', json_build_object(
                        'stratum_name', '{stratum_name}',
                        'stratum_id', s_id::text,
                        'queen_id', q_id::text
                    )::text);
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """))

            await conn.execute(text(f"DROP TRIGGER IF EXISTS trg_notify_new_asset ON {schema_name}.assets;"))
            await conn.execute(text(f"""
                CREATE TRIGGER trg_notify_new_asset
                AFTER INSERT ON {schema_name}.assets
                FOR EACH ROW EXECUTE FUNCTION {schema_name}.notify_new_asset();
            """))
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.rex_extraction (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    asset_id UUID REFERENCES {schema_name}.assets(id) ON DELETE CASCADE UNIQUE,
                    areum_node_id VARCHAR(255) NOT NULL,
                    source_url TEXT,
                    source_url_hash VARCHAR(64),
                    extracted_json JSONB NOT NULL,
                    confidence_score FLOAT NOT NULL,
                    requires_premium BOOLEAN DEFAULT FALSE,
                    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.target_sites (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    domain VARCHAR(255) UNIQUE NOT NULL,
                    display_name VARCHAR(255),
                    playbook TEXT,
                    scout_strategy VARCHAR(50) DEFAULT 'DOM_CRAWL',
                    scout_config JSONB DEFAULT '{{}}'::jsonb,
                    priority INT DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_scouted_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.scout_jobs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    target_site_id UUID REFERENCES {schema_name}.target_sites(id),
                    status VARCHAR(50) DEFAULT 'RUNNING',
                    urls_discovered INT DEFAULT 0,
                    urls_queued INT DEFAULT 0,
                    error_msg TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    finished_at TIMESTAMP WITH TIME ZONE
                );
            """))
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.scout_history (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    url TEXT NOT NULL,
                    domain VARCHAR(255) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    scout_job_id VARCHAR(100), -- [V51.5] SHADOW-JOB-AUTO support
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    UNIQUE(url)
                );
            """))
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.areum_extraction (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    asset_id UUID REFERENCES {schema_name}.assets(id) ON DELETE CASCADE UNIQUE,
                    extracted_data JSONB NOT NULL,
                    confidence_score FLOAT NOT NULL,
                    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.premium_enhanced (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    areum_extraction_id UUID REFERENCES {schema_name}.areum_extraction(id) ON DELETE CASCADE,
                    enhanced_metadata JSONB DEFAULT '{{}}'::jsonb,
                    ai_model VARCHAR(100),
                    enhanced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.pipeline_tasks (
                    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    stratum_id VARCHAR(100) NOT NULL,
                    target_url TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'PENDING',
                    payload_locator TEXT,
                    payload_hash VARCHAR(64),
                    cost_cents FLOAT DEFAULT 0.0,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))

            # [ADVANCED DOMAIN] High-Fidelity Labeling & Compilation tables
            if stratum_name == "recilabel":
                await conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {schema_name}.master_taxonomy (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        label_type VARCHAR(50) NOT NULL, -- 'INGREDIENT', 'TASTE', 'METHOD', 'CULTURE'
                        label_name VARCHAR(255) UNIQUE NOT NULL,
                        physical_constants JSONB DEFAULT '{{}}'::jsonb,
                        is_canonical BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """))
                await conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {schema_name}.recipe_compilations (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        asset_id UUID NOT NULL,
                        compilation_log JSONB NOT NULL, -- The "Compiled to Machine Commands" dump
                        flavor_vector JSONB, -- The 8-point scalar taste profile
                        identity_integrity_score FLOAT,
                        compiled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """))
                await conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {schema_name}.machine_commands (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        compilation_id UUID REFERENCES {schema_name}.recipe_compilations(id) ON DELETE CASCADE,
                        sequence_order INT NOT NULL,
                        action_type VARCHAR(50) NOT NULL,
                        target_temp FLOAT,
                        duration_sec INT,
                        params JSONB DEFAULT '{{}}'::jsonb
                    );
                """))
                logger.info(f"[PROVISIONER] High-Fidelity Labeling Tables injected into {schema_name}")
        await AuditLogger.log_movement(
            action_type="PROVISION-STRATUM",
            source="Provisioner.create_stratum_space",
            target=schema_name,
            reason=f"New Stratum created: {stratum_name}"
        )
        logger.info(f"[PROVISIONER] Stratum {schema_name} provisioned successfully.")

    @staticmethod
    async def create_registry_space():
        """전사 엔티티 레지스트리 스키마 생성 — API Contract v2.0"""
        logger.info("[PROVISIONER] Creating schema_registry v2.0...")
        async with engine.begin() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS schema_registry;"))

            # [v2.0] Idempotency-Key deduplication store (72h TTL enforced by scheduler)
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_registry.idempotency_keys (
                    idempotency_key VARCHAR(255) PRIMARY KEY,
                    entity_id       UUID NOT NULL,
                    entity_type     VARCHAR(50) NOT NULL,
                    created_at      TIMESTAMPTZ DEFAULT NOW()
                );
            """))

            # [Absolute Sequencer] 제국 헌법에 따른 고유 ID 순차 발급용 카운터
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_registry.sequences (
                    entity_class    VARCHAR(50) PRIMARY KEY, -- 예: QUEEN-IN, QUEEN-ALLY, ANT-USER, STRATUM 등
                    current_value   INT DEFAULT 0,
                    updated_at      TIMESTAMPTZ DEFAULT NOW()
                );
            """))
            
            # 기본 카운터 초기화 (없으면 삽입)
            await conn.execute(text("""
                INSERT INTO schema_registry.sequences (entity_class, current_value)
                VALUES 
                    ('MONEWMENT', 1),    -- 0은 코어 전용이므로 1부터 (실제로는 MONEWMENT-1부터 격상됨)
                    ('STRATUM', 1),
                    ('QUEEN-IN', 1),
                    ('QUEEN-ALLY', 1),
                    ('ANT-USER', 1),
                    ('ANT-AP', 1),
                    ('ANT-CODE', 1),
                    ('AREUM-IN', 1),
                    ('AREUM-ALLY', 1)
                ON CONFLICT (entity_class) DO NOTHING;
            """))

            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_registry.monewments (
                    monewment_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    display_name    VARCHAR(255) NOT NULL,
                    owner_user_id   VARCHAR(255) NOT NULL,
                    host_machine_id VARCHAR(255),
                    core_version    VARCHAR(50),
                    status          VARCHAR(50) DEFAULT 'ACTIVE',
                    total_stratum_count INT DEFAULT 0,
                    uptime_seconds  BIGINT DEFAULT 0,
                    fencing_token   BIGINT DEFAULT 1,
                    predecessor_id  UUID,
                    death_reason    VARCHAR(100),
                    born_at         TIMESTAMPTZ DEFAULT NOW(),
                    last_seen_at    TIMESTAMPTZ DEFAULT NOW(),
                    died_at         TIMESTAMPTZ
                );
            """))

            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_registry.stratums (
                    stratum_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    stratum_name    VARCHAR(255) NOT NULL,
                    monewment_id    UUID REFERENCES schema_registry.monewments(monewment_id),
                    purpose         TEXT,
                    schema_pg       VARCHAR(100),
                    cloud_ai_enabled BOOLEAN DEFAULT FALSE,
                    total_cost_cents FLOAT DEFAULT 0.0,
                    accumulated_cost FLOAT DEFAULT 0.0, -- [V51.5] Decentralized cost tracking
                    budget_limit     FLOAT DEFAULT 1000000000.0, -- [V51.5] Automatic Kill-Order threshold
                    queen_count     INT DEFAULT 0,
                    status          VARCHAR(50) DEFAULT 'ACTIVE',
                    fencing_token   BIGINT DEFAULT 1,
                    predecessor_id  UUID,
                    death_reason    VARCHAR(100),
                    born_at         TIMESTAMPTZ DEFAULT NOW(),
                    last_seen_at    TIMESTAMPTZ DEFAULT NOW(),
                    died_at         TIMESTAMPTZ,
                    UNIQUE(monewment_id, stratum_name)
                );
            """))

            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_registry.queens (
                    queen_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    queen_name      VARCHAR(255) NOT NULL,
                    stratum_ids     UUID[] DEFAULT '{}',
                    relationship_type VARCHAR(50) DEFAULT 'INTERNAL',
                    queen_type      VARCHAR(50) DEFAULT 'GENERAL',
                    api_key_masked  VARCHAR(20),
                    active_ant_count INT DEFAULT 0,
                    total_tasks_completed INT DEFAULT 0,
                    host_ip         VARCHAR(100),
                    status          VARCHAR(50) DEFAULT 'ACTIVE',
                    accumulated_cost FLOAT DEFAULT 0.0, -- [V51.5]
                    budget_limit     FLOAT DEFAULT 1000000.0,  -- [V51.5]
                    fencing_token   BIGINT DEFAULT 1,
                    predecessor_id  UUID,
                    death_reason    VARCHAR(100),
                    born_at         TIMESTAMPTZ DEFAULT NOW(),
                    last_seen_at    TIMESTAMPTZ DEFAULT NOW(),
                    died_at         TIMESTAMPTZ
                );
            """))

            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_registry.ants (
                    ant_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    ant_name        VARCHAR(255) NOT NULL,
                    queen_id        UUID REFERENCES schema_registry.queens(queen_id),
                    stratum_id      UUID,
                    ant_type        VARCHAR(50) DEFAULT 'CODE',
                    task_id         UUID,
                    target_url      TEXT,
                    payload_hash    VARCHAR(64),
                    items_collected INT DEFAULT 0,
                    error_message   TEXT,
                    status          VARCHAR(50) DEFAULT 'RUNNING',
                    fencing_token   BIGINT DEFAULT 1,
                    predecessor_id  UUID,
                    death_reason    VARCHAR(100),
                    total_cost_cents FLOAT DEFAULT 0.0,
                    born_at         TIMESTAMPTZ DEFAULT NOW(),
                    last_seen_at    TIMESTAMPTZ DEFAULT NOW(),
                    died_at         TIMESTAMPTZ,
                    accumulated_cost FLOAT DEFAULT 0.0, -- [V51.5]
                    budget_limit     FLOAT DEFAULT 1000000.0,  -- [V51.5]
                    UNIQUE(stratum_id, ant_name)
                );
            """))

            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_registry.areums (
                    areum_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    areum_name      VARCHAR(255) NOT NULL,
                    stratum_id      UUID NOT NULL,
                    queen_id        UUID REFERENCES schema_registry.queens(queen_id),
                    ollama_model    VARCHAR(100) DEFAULT 'gemma3:4b',
                    status          VARCHAR(50) DEFAULT 'ACTIVE',
                    fencing_token   BIGINT DEFAULT 1,
                    predecessor_id  UUID,
                    death_reason    VARCHAR(100),
                    born_at         TIMESTAMPTZ DEFAULT NOW(),
                    last_seen_at    TIMESTAMPTZ DEFAULT NOW(),
                    died_at         TIMESTAMPTZ,
                    UNIQUE(stratum_id, areum_name)
                );
            """))

            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_registry.data_movements (
                    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    timestamp       TIMESTAMPTZ DEFAULT NOW(),
                    action_type     VARCHAR(50) NOT NULL, -- e.g. 'L1_PURGE'
                    source_location TEXT,
                    target_location TEXT,
                    record_count    INT DEFAULT 0,
                    sample_hash     VARCHAR(64),
                    reason          TEXT
                );
            """))

        await AuditLogger.log_movement(
            action_type="PROVISION-REGISTRY",
            source="Provisioner.create_registry_space",
            target="schema_registry",
            reason="Imperial Registry v2.0 initialized"
        )
        logger.info("[PROVISIONER] schema_registry v2.0 provisioned successfully.")

    @staticmethod
    async def create_system_space():
        """제국 행정/치안 전담 특수 영토(STRATUM-SYSTEM) 스키마 생성"""
        schema_name = "schema_system"
        logger.info(f"[PROVISIONER] Creating Imperial System space: {schema_name}")
        async with engine.begin() as conn:
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name};"))
            # [SECURITY] Global Kill Switch table
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.system_config (
                    is_emergency_shutdown BOOLEAN DEFAULT FALSE,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            # Insert initial record if not exists
            await conn.execute(text(f"""
                INSERT INTO {schema_name}.system_config (is_emergency_shutdown)
                SELECT FALSE WHERE NOT EXISTS (SELECT 1 FROM {schema_name}.system_config);
            """))
        await AuditLogger.log_movement(
            action_type="PROVISION-SYSTEM-STRATUM",
            source="Provisioner.create_system_space",
            target=schema_name,
            reason="Imperial Civil Service Stratum provisioned"
        )
        logger.info(f"[PROVISIONER] Stratum {schema_name} provisioned successfully.")

    @staticmethod
    async def create_pipeline_space():
        """REX 글로벌 분석망 및 AREUM 추적 스키마 생성"""
        logger.info("[PROVISIONER] Creating schema_pipeline (REX/AREUM pipeline)...")
        async with engine.begin() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS schema_pipeline;"))

            # AREUM 인스턴스 레지스트리 (각 AREUM의 소속 STRATUM 및 상태 추적)
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_pipeline.areum_registry (
                    areum_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    areum_name      VARCHAR(255) NOT NULL,
                    stratum_id      UUID,
                    queen_id        UUID,
                    ollama_model    VARCHAR(100) DEFAULT 'gemma3:4b',
                    status          VARCHAR(50) DEFAULT 'ACTIVE',
                    reports_sent    INT DEFAULT 0,
                    last_report_at  TIMESTAMPTZ,
                    born_at         TIMESTAMPTZ DEFAULT NOW(),
                    last_seen_at    TIMESTAMPTZ DEFAULT NOW()
                );
            """))

            # REX 메타 분석 수신 테이블 (AREUM이 분석 완료 후 이 테이블에 적재)
            # REX는 오직 이 테이블만 바라보며 다중 영토 트렌드를 융합한다.
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_pipeline.cross_reports (
                    report_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    areum_id        UUID REFERENCES schema_pipeline.areum_registry(areum_id),
                    stratum_id      UUID NOT NULL,
                    source_asset_id UUID,
                    ollama_model    VARCHAR(100),
                    confidence_score FLOAT NOT NULL CHECK (confidence_score BETWEEN 0.0 AND 1.0),
                    keywords        JSONB DEFAULT '[]'::jsonb,
                    summary         TEXT NOT NULL,
                    raw_essence     JSONB,
                    rex_consumed    BOOLEAN DEFAULT FALSE,
                    rex_consumed_at TIMESTAMPTZ,
                    rex_processing  BOOLEAN NOT NULL DEFAULT FALSE,
                    rex_processed_at TIMESTAMPTZ,
                    created_at      TIMESTAMPTZ DEFAULT NOW()
                );
            """))



            # REX 소비 속도를 위한 인덱스
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_cross_reports_unconsumed
                ON schema_pipeline.cross_reports (rex_consumed, created_at)
                WHERE rex_consumed = FALSE;
            """))

            # [PHASE 10] Strategic Decrees - The distilled wisdom of the Empire
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_pipeline.strategic_decrees (
                    decree_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    strategic_directive TEXT NOT NULL,
                    focus_sector    VARCHAR(100),
                    correlations    JSONB DEFAULT '[]'::jsonb,
                    source_ref_ids  JSONB DEFAULT '[]'::jsonb, -- UUIDs of reports that led to this decree
                    payload_hash    VARCHAR(64),
                    created_at      TIMESTAMPTZ DEFAULT NOW()
                );
            """))

        logger.info("[PROVISIONER] schema_pipeline provisioned successfully.")

    @staticmethod
    async def create_pim_space():
        """AREUM-IN-1 전용 텍스트 정규화(PIM) 스키마 생성"""
        logger.info("[PROVISIONER] Creating schema_pim (Ingredient Normalization)...")
        async with engine.begin() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS schema_pim;"))
            
            # AREUM-IN이 정규화에 성공한 표준 식재료 매핑 데이터
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_pim.areum_vas_outputs (
                    vas_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    asset_id UUID NOT NULL,
                    raw_text VARCHAR(255) NOT NULL,
                    canonical_id VARCHAR(100),
                    meta_origin VARCHAR(50), 
                    meta_state VARCHAR(50),
                    meta_detail VARCHAR(50),
                    base_water_pct FLOAT,
                    base_fat_pct FLOAT,
                    protein_denature_c FLOAT
                );
            """))

            # AREUM-IN이 판독에 실패하여 V-Learning (Consensus)으로 이관된 텍스트
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_pim.residues (
                    hash_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    raw_text VARCHAR(255) NOT NULL,
                    frequency INT DEFAULT 1,
                    status VARCHAR(20) DEFAULT 'PENDING' -- PENDING, RATIFIED
                );
            """))
            
        logger.info("[PROVISIONER] schema_pim provisioned successfully.")

    @staticmethod
    async def create_archive_space():
        """[DECREE 11: ETERNAL ASSET] 영구 비축을 위한 아카이브 스키마 생성"""
        logger.info("[PROVISIONER] Creating schema_archive (Imperial Eternal Archive)...")
        async with engine.begin() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS schema_archive;"))
            
            # 원본 자산 백업 테이블 (vendors.raw_archive의 물리적 미러)
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_archive.eternal_assets (
                    archive_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    original_id     VARCHAR(255),
                    url             TEXT NOT NULL,
                    content_hash    VARCHAR(64),
                    raw_html_gz     BYTEA,
                    archived_at     TIMESTAMPTZ DEFAULT NOW()
                );
            """))
            
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_archive_hash ON schema_archive.eternal_assets(content_hash);"))
            
        logger.info("[PROVISIONER] schema_archive provisioned. Assets are now SECURED.")

    @staticmethod
    async def create_rex_space():
        """[V43 REX] 최상위 지능 포식자 스키마 및 가변 지식 저장소 (Ollama Integration) 생성"""
        logger.info("[PROVISIONER] Creating schema_rex (Absolute Intelligence Space)...")
        async with engine.begin() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS schema_rex;"))
            
            # AREUM 들이 바치는 이질적인 지능 보고서를 수용하는 가변 테이블
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_rex.areum_reports (
                    report_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    areum_id        VARCHAR(255) NOT NULL,
                    report_type     VARCHAR(100) NOT NULL, -- e.g. 'INGREDIENT_TAXONOMY', 'BEHAVIOR_ANALYSIS'
                    raw_payload     JSONB NOT NULL,
                    stratum_id      VARCHAR(255),
                    received_at     TIMESTAMPTZ DEFAULT NOW(),
                    processing_status VARCHAR(50) DEFAULT 'PENDING'
                );
            """))

            # ORCHESTRA-ANT가 관리하는 Ollama 학습/주입 대기열
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_rex.learning_queue (
                    queue_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    report_id       UUID REFERENCES schema_rex.areum_reports(report_id) ON DELETE CASCADE,
                    target_model    VARCHAR(100) DEFAULT 'llama3',
                    priority        INT DEFAULT 0,
                    status          VARCHAR(50) DEFAULT 'QUEUED', -- QUEUED, IN_PROGRESS, ASSIMILATED, FAILED
                    orchestrator_id VARCHAR(255), -- ANT-MANAGER ID
                    queued_at       TIMESTAMPTZ DEFAULT NOW(),
                    processed_at    TIMESTAMPTZ
                );
            """))
            
        await AuditLogger.log_movement(
            action_type="PROVISION-REX-STRATUM",
            source="Provisioner.create_rex_space",
            target="schema_rex",
            reason="Absolute Intelligence (REX) schema provisioned"
        )
        logger.info("[PROVISIONER] schema_rex provisioned successfully.")

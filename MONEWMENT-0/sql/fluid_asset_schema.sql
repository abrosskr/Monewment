-- [IMPERIAL DECREE: DB LAYER V2]
-- Physical Schema for Fluid Assets with Schemaless Ingestion Support

-- NOTE: {X} should be replaced with the actual Stratum ID or Name
CREATE SCHEMA IF NOT EXISTS schema_stratum_0;

CREATE TABLE IF NOT EXISTS schema_stratum_0.assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_origin VARCHAR(255),  -- 데이터의 출처 (URL, File Path 등)
    data_type VARCHAR(50),       -- NOVEL, RECIPE, COMMERCE 등 구분자
    
    -- [CORE] 가변형 파라미터의 심장
    raw_payload JSONB NOT NULL,  -- 원시 데이터 전체 (필드 수/길이 무관)
    metadata JSONB,              -- 수집 시점의 환경 변수 및 부가 정보
    
    is_processed BOOLEAN DEFAULT FALSE,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ai_summary TEXT              -- AREUM이 사후에 채워넣을 필드
);

-- [PERFORMANCE] GIN Index for Schemaless Ingestion
-- 비정형 데이터(JSONB)의 탐색 엔트로피를 최소화하고 대칭적 검색 속도를 확보함.
CREATE INDEX IF NOT EXISTS idx_assets_raw_payload ON schema_stratum_0.assets USING GIN (raw_payload);
CREATE INDEX IF NOT EXISTS idx_assets_processed ON schema_stratum_0.assets (is_processed) WHERE is_processed = FALSE;

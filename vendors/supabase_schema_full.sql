-- [VENDORS FULL SCHEMA]
-- 이 스크립트는 Vendors 시스템의 'Log(기록)'와 'Intelligence(지능)'을 모두 담당합니다.

-- 1. 확장 기능 활성화 (필수)
-- 벡터 검색을 위해 pgvector를 켭니다. 이게 없으면 "지능형 검색"이 불가능합니다.
create extension if not exists vector;

-- 2. 조리 세션 (Cooking Sessions) - [기존 제안 유지]
create table cooking_sessions (
  id uuid default gen_random_uuid() primary key,
  started_at timestamptz default now(),
  device_id text not null,
  recipe_name text,
  metadata jsonb
);

-- 3. 물리 상태 로그 (Physics Vector Logs) - [기존 제안 유지]
create table physics_logs (
  id bigint generated always as identity primary key,
  session_id uuid references cooking_sessions(id) on delete cascade,
  logged_at timestamptz default now(),
  temp float not null,
  velocity float,
  accel float,
  integral float,
  time_idx float
);
create index idx_logs_session on physics_logs(session_id);

-- [누락된 핵심 기능 1] 레시피 지능 (Recipe Intelligence)
-- 텍스트 검색만이 아니라 의미 기반 검색(Vector Search)을 위해 필수입니다.
create table recipes (
  id uuid default gen_random_uuid() primary key,
  title text not null,
  raw_content text, -- 원본 HTML/텍스트
  structured_data jsonb, -- 정제된 JSON
  
  -- 핵심: 768차원 또는 1536차원 임베딩 벡터 (모델에 따라 조정)
  embedding vector(768), 
  
  source_url text,
  created_at timestamptz default now()
);
-- 벡터 인덱스 (HNSW: 고속 검색용)
create index on recipes using hnsw (embedding vector_cosine_ops);

-- [누락된 핵심 기능 2] 스토리지 정책 (Storage Policies)
-- SQL만으로는 Bucket이 생성되지 않지만, RLS 정책은 여기서 미리 잡아둘 수 있습니다.
-- 실제 Bucket('fis-logs', 'recipe-images')은 대시보드 Storage 메뉴에서 생성해야 합니다.

-- [보안 설정] Row Level Security (RLS)
-- 일단 개발 편의를 위해 익명(Anon) 쓰기를 허용하거나, Service Role 키를 써야 합니다.
alter table cooking_sessions enable row level security;
alter table physics_logs enable row level security;
alter table recipes enable row level security;

-- (개발용) 모든 접근 허용 정책 (서비스 오픈 전에는 이렇게 테스트)
create policy "Allow all access" on cooking_sessions for all using (true) with check (true);
create policy "Allow all access" on physics_logs for all using (true) with check (true);
create policy "Allow all access" on recipes for all using (true) with check (true);

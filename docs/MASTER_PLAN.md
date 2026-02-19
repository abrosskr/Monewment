🏛️ [MASTERPLAN] Monewment V3: Digital Twin & Multi-Tenant PaaS Cluster
"서비스를 위한 서비스, 제로 엔트로피(Zero-Entropy) 인프라스트럭처"

1. 시스템 존재론 (System Ontology: 3-Depth)
Monewment는 단일 애플리케이션이 아닙니다. 수많은 하위 프로젝트와 이종 기기들을 수용하는 '운영체제'와 같습니다.

Depth 1. Monewment (The Control Plane & Gateway):

역할: 전체 클러스터의 '조물주'이자 '단일 검문소'.

기능: 모든 외부 트래픽을 포트 8800 하나로 받아내어(Tenant Dispatcher), 요청자가 어떤 방(Queen) 소속인지 판별하고 해당 방의 DB와 격리된 로직으로 라우팅합니다.

Depth 2. Queen (The Tenant Room / Sandbox):

역할: vendors나 '스마트 팩토리 A'와 같은 개별 서비스/프로젝트가 입주하는 독립된 영토.

기능: Supabase 내의 완벽히 격리된 전용 스키마(schema_queen_xxx)를 부여받으며, Monewment가 기본 제공하는 필수 모듈(Auth, Backup 등)을 상속받습니다.

Depth 3. Ant (The Endpoints):

역할: 데이터를 발생시키거나 서비스를 소비하는 최종 노드.

기능: 사람(Web/App), 이종 기기(AX8 열화상 카메라), 자동화 봇 등. 이들은 Monewment의 Adaptor를 통해 각자의 Queen에게 데이터를 쏘아 보냅니다.

2. 제로 엔트로피 인프라스트럭처 (Physical Architecture)
과거의 패착(포트 충돌, 하드코딩 지옥, 보안 누수)을 물리적으로 차단한 기반 설계입니다.

단일 관문 라우팅 (Single-Port Gateway):

새로운 프로젝트가 1,000개 생겨도 포트 번호를 추가하지 않습니다. 오직 8800번 포트만 개방하며, HTTP 헤더(X-Queen-ID)나 URL Path를 통해 논리적으로 트래픽을 분배합니다. (기존 vendors는 8000번 단독 주택에 그대로 공존 가능).

강타입 환경 변수 주입 (Strict Dependency Injection):

pydantic-settings를 통해 시스템 기동 시점에 .env의 타입을 엄격히 검사합니다. 하드코딩은 단 한 줄도 허용하지 않습니다.

블랙박스 보안망 (Zero-Trust Masking):

최상위 스트림(sys.stdout/stderr)을 가로채어, 개발 중 에러가 발생하더라도 DB 비밀번호나 JWT 토큰이 평문으로 로그에 찍히는 것을 원천 봉쇄합니다.

3. 3대 핵심 엔진 (The 3 Core Engines)
디지털 트윈 시나리오(사용자 코드 마운트 및 IoT 데이터 수집)를 실현하기 위한 심장부입니다.

The Dispatcher (라우팅 엔진 - 🟢 완료):

모든 요청의 Queen-ID를 추출해 ContextVar에 단기 기억으로 박제하여, 데이터가 섞이는 참사(Data Bleed)를 막습니다.

The Provisioner (공간 창조 엔진 - 🟡 대기 중):

입주 신청 시 Supabase(PostgreSQL)에 CREATE SCHEMA를 실행하여 물리적 DB 공간을 찍어내고, 공통 필수 테이블(회원, 결제, 로그)을 자동 세팅합니다.

The Sandbox (디지털 트윈 실행 엔진 - ⚪ 예정):

사용자가 복사+붙여넣기 한 파이썬 코드나 제어 로직을 무거운 VM이 아닌 초경량 Docker 컨테이너에 격리(Mount)하여 안전하게 실행합니다. (CPU/RAM 물리적 제한 강제).

4. 입주 시나리오: 프로젝트 'Vendors'의 마이그레이션
vendors를 Monewment 클러스터의 첫 번째 정식 입주자(Alpha Tenant)로 격상시키는 절차입니다.

Step 1: Provisioner 엔진을 통해 queen_vendors라는 독립 스키마를 Monewment DB 내부에 생성합니다.

Step 2: vendors의 고유 테이블 구조를 이 스키마에 이식합니다.

Step 3: 기존 vendors의 데이터를 마이그레이션합니다.

Step 4: API 호출 주소를 http://...:8000/에서 http://...:8800/vendors/로 변경하여 Monewment 게이트웨이 산하로 완전히 통합합니다.

5. 실행 로드맵 (Execution Roadmap)
Phase 1: 기반 시설 공사 (Mise en place) - ✅ 완료

문서 자동화 CCTV, .env 통제, 마스킹 로거, 포트 규약(8800), 테넌트 디스패처 구축.

Phase 2: 공간 창조 (Provisioning) - 🚀 Next Step

src/core/provisioner.py 구축. Supabase 동적 스키마 생성 및 공통 테이블(Auth) 배포 로직 완성.

Phase 3: 입주 및 마이그레이션 (Onboarding)

vendors 프로젝트 스키마 이식 및 라우팅 연동 테스트.

Phase 4: 디지털 트윈 샌드박스 (The Sandbox)

IoT 기기(AX8) 데이터 수집용 Edge Adaptor 신설 및 사용자 정의 코드 안전 실행 환경(Docker 마운트) 구축.
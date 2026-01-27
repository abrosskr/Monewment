# Supabase 기반 3-Tier 아키텍처: Dual-Core Strategy

## 1. 사용자의 제안 (The Game Changer)
> "Supabase는 기본 2개의 무료 프로젝트를 제공한다. 이 두 개와 로컬 Edge를 나눠서 운영하면 어때?"

**분석 결과**: **매우 탁월한 전략(Brilliant Strategy)**입니다.
단일 프로젝트(500MB)의 한계를 물리적으로 2배(1GB)로 늘리면서, **"실험실(Lab)"**과 **"매장(Live)"**을 완벽하게 격리할 수 있습니다.

## 2. 3-Tier 아키텍처 정의

우리는 이제 3개의 물리적 공간을 가집니다.

| Tier | 명칭 (Alias) | 역할 | 저장 데이터 |
| :--- | :--- | :--- | :--- |
| **Tier 1 (Local)** | **The Kitchen (Edge)** | **생산 및 연산** | Raw Video, TSV 실시간 연산, 로컬 캐시 |
| **Tier 2 (Cloud A)** | **The Lab (Brain)** | **수집 및 학습** | Scraping Raw Data, 모든 조리 세션 로그(TSV), 실험적 모델 |
| **Tier 3 (Cloud B)** | **The Restaurant (Live)** | **서비스 및 배포** | 검증된 Golden Recipe, 사용자 프로필, 최종 모델 가중치 |

## 3. 데이터 흐름 (Data Flow)

### Step 1: 수집 및 실험 (Kitchen -> Lab)
1.  **Edge**가 10Hz 데이터를 TSV로 변환.
2.  변환된 모든 데이터를 **[Cloud A: Lab]**으로 전송.
    - 여기는 500MB가 꽉 찰 때까지 마음껏 데이터를 쌓습니다. ("더러운" 데이터도 OK)
    - 수집된 웹 레시피(Raw Text)도 여기에 저장합니다.

### Step 2: 학습 및 정제 (Inside Lab)
1.  **AI(별도 로컬 PC 또는 Colab)**가 **[Cloud A]**에 접속하여 데이터를 가져옵니다.
2.  학습을 통해 "Golden Standard"를 추출합니다.

### Step 3: 배포 (Lab -> Live)
1.  검증된 Golden Model(최종 결과물)만 **[Cloud B: Live]**로 복사(Migration)합니다.
2.  **[Cloud B]**는 500MB를 아주 아껴서 사용하므로, 절대 용량이 부족하지 않습니다.

### Step 4: 서비스 (Live -> User)
1.  사용자(앱)는 오직 **[Cloud B]**에만 접속합니다.
2.  실험 데이터나 노이즈가 없는 쾌적한 환경을 제공합니다.

## 4. 상세 구성안

### Project A: `vendors-brain` (Lab)
- **DB**: `scraped_recipes` (Raw Text), `session_logs` (All TSV)
- **Storage**: `raw-datasets`
- **Auth**: 관리자(Developer) 전용

### Project B: `monewment-live` (Restaurant)
- **DB**: `golden_recipes` (Verified), `users`, `inventory`
- **Storage**: `recipe-thumbnails` (Public)
- **Auth**: 일반 사용자(Chef) 접속

## 5. 결론
이 **"Dual-Core + Edge"** 전략은 무료 티어의 혜택을 극대화(100% 활용)하는 최적의 해법입니다.
- **용량 2배**: 1GB (500MB x 2)
- **안정성**: 수집 중 발생할 수 있는 DB 부하가 서비스(User)에 전혀 영향을 주지 않음.

**다음 단계**: Supabase에서 프로젝트 2개를 생성하고(`vendors-brain`, `monewment-live`), 각각의 Key를 발급받아 환경 설정을 진행합니다.

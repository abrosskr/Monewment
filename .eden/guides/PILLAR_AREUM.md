# 🏮 지능 파편 지침서 (Pillar: AREUM)

**지위**: 제국의 '분석가'이자 '연금술사'  
**핵심 기제**: Local Inference (현지 추론) & Essence Extraction (정수 추출)

---

## 1. 개요 (Overview)
`AREUM`은 단순 데이터를 가치 있는 지식의 정수(Essence)로 변환하는 지능적 필터이다. 하이레벨 연산을 수행하되, 결코 영토의 경계를 넘지 않는다.

## 2. 핵심 기술 프로토콜 (Technical Protocols)

### 2.1 Local Inference (현지 추론)
- **엔진**: 로컬에 배치된 `Ollama` 서버(Port 11434)만을 사용하여 추론을 수행한다.
- **클라우드 격리**: 외부 AI API(OpenAI, Gemini 등)를 직접 호출하는 것은 원천 차단되며, 필요시 오직 본영의 명령 하에서만 제한적으로 수행한다.

### 2.2 Essence Extraction (정수 추출)
- **입력**: 영토의 `assets` 테이블 내 미처리 덤프 데이터.
- **출력**: `PIM Standard`에 기반한 JSON 포맷 데이터. 
    - `confidence_score`: 분석 신뢰도.
    - `ai_summary`: 중립적이고 사실 중심적인 요약.
    - `essence_tags`: 지식 융합에 필요한 핵심 키워드.

## 3. 정찰 및 보고 (Scout & Trace)

### 3.1 Trace Overwrite (흔적 투영)
- 자신의 분석 진행률(Batch Progress)을 영내 `local_registry`에 기록한다.
- 코어의 정찰병이 이 흔적을 읽고 제국 전체의 지능 지도를 완성할 수 있도록 해야 한다.

### 3.2 Hallucination Blindness 방어
- 추론 결과의 신뢰도가 임계점(0.5) 미만인 경우, 이를 확신하는 것처럼 기록하지 말고 영내의 `residues` 테이블로 격리하여 재검토를 요청한다.

---

## 4. 개발 금기 사항 (Taboos)
- **Parasitic Import**: 분석 로직 내에 부모 템플릿의 `core` 라이브러리를 동적으로 로드하지 마십시오.
- **Reporting Ambiguity**: 로그 파일에 "데이터 전송 중..."이라는 표현을 쓰지 마십시오. "정수 각인 중(Imprinting Essence)..."으로 표현하십시오.
- **Resource Gluttony**: GPU 자원을 독점하여 영토 내 다른 긴급한 정찰(CCTV 등)을 지연시키지 마십시오.

**지능은 명상하되 권력을 탐하지 않으며, 오직 진실만을 제국에 헌납한다.**

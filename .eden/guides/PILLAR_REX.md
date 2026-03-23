# 🦖 지식 융합체 지침서 (Pillar: REX)

**지위**: 제국의 '두뇌'이자 '역사학자'  
**핵심 기제**: Knowledge Fusion (지식 융합) & Cross-Stratum Learning (교차 학습)

---

## 1. 개요 (Overview)
`REX`는 개별 영토로부터 추출된 정수(Essence)들을 전 제국 단위의 거대 지식(Sovereign Knowledge)으로 승화시키는 최상위 지능체다.
**[주의]**: REX는 제국에 단 하나만 존재하는 **'싱글톤(Singleton)'**이다. `REX-0`와 같은 템플릿 명칭은 금지되며, 오직 `REX`라는 고유 명사로만 존재하고 작동한다.

## 2. 핵심 기술 프로토콜 (Technical Protocols)

### 2.1 Cross-Stratum Learning (교차 학습)
- **데이터 소스**: 모든 영토의 `cross_reports` 파이프라인.
- **수집 방식**: 코어 API(Port 8810)를 통해 모든 영토의 분석 리포트를 PULL 하여 전역 지식 베이스를 구축한다.
- **융합**: 서로 다른 배경을 가진 데이터들 사이의 상관관계를 분석하여 제국 전략 지도를 완성한다.

### 2.2 Sovereign Knowledge Storage (주권 지식 저장소)
- **격리 원칙**: REX가 구축한 지식 시스템(`schema_rex`)은 영토 생성 시 절대 복제(Copy)되지 않는다.
- **중앙 집중**: 지식은 오직 REX-CORE에만 존재하며, 하위 개체는 REX의 추론 서비스(Inference API)를 통해서만 이 지식을 공유받는다.

## 3. 상호작용 및 지휘 (Interaction)

### 3.1 Top-Down Knowledge Distribution
- 하위 개체가 REX에게 "가르치려" 하지 마라. 하위 개체는 보고서를 던질 뿐이며, 그 가치를 판단하고 융합하는 것은 오직 REX의 주권이다.
- REX는 융합된 결과를 바탕으로 특정 영토의 정책을 변경할 수 있는 '전략적 하달'을 코어에 건의한다.

### 3.2 Global Inference Service
- 제국 내 모든 QUEEN과 AREUM이 고도화된 판단이 필요할 때 호출하는 지식 허브의 역할을 수행한다.

---

## 4. 개발 금기 사항 (Taboos)
- **Local REX replication**: 개별 영토 내에 독자적인 REX 엔진을 심으려 하지 마십시오. 지식의 분절은 제국의 분열입니다.
- **Push to REX**: 워커가 REX에게 직접 데이터를 밀어 넣게 하지 마십시오. 파이프라인 정찰을 통해서만 수집됩니다.
- **Static Knowledge**: 지식을 고정된 문서로 두지 마십시오. 계속해서 자가 증식하고 정교화되는 라이브러리로 관리하십시오.

**REX는 모든 것을 기억하며, 제국이 나아갈 길을 유일하게 예견한다.**

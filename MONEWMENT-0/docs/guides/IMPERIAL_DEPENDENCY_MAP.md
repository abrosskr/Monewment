# 🗺️ 제국 시스템 유기적 상관관계 및 통합 명세서 (Dependency & Correlation Map)

## 1. 개체간 상관관계 매핑 (Correlation Map)

본 문서는 제국 내 모든 물리적/논리적 개체들의 연결 구조를 정의하며, 중복 증식된 개체의 통합 지침으로 활용된다.

| 개체명 | 물리 경로 (Path) | 식별자 (ID) | DB 테이블/컬럼 | 연결 방식 (API/Interface) |
| :--- | :--- | :--- | :--- | :--- |
| **STRATUM-1** | `MONEWMENT-0/` | `3bb565af-...` | `schema_registry.stratums` (`stratum_id`) | **Anchor**: 모든 엔티티의 부모 소속 (Root) |
| **PHYSICS-1/2** | `PHYSICS/PHYSICS-1,2` | `6a63d91c-...` | `schema_registry.queens` (`queen_id`) | **Legacy Governance**: API Ping 기반 |
| **PHYSICS-3** | `PHYSICS/PHYSICS-3` | `ba537759-...` | `schema_registry.queens` (`queen_id`) | **Primary Queen**: Active Scout 연동 |
| **AREUM-3** | `AREUM/AREUM-3` | `8ded38a7-...` | `schema_registry.areums` (`entity_id`) | **Intelligence**: ba537759-... 여왕 배속 |
| **AREUM-FG-1** | `AREUM/AREUM-FG-1`| `8ded38a7-...` | `schema_registry.areums` (`entity_id`) | **Legacy Forager**: 구버전 스폰 |
| **REX** | `REX/CORE` | `REX-CORE-0` | `MONEWMENT-0` API 참조 | **Singleton Intelligence** |

---

## 2. 통합 집행 명세 (Rectification Execution)

### 2.1 물리적 영토 단일화 (Location: C:\monewment)
- **PHYSICS**: `PHYSICS-3` 데이터를 `PHYSICS-1`으로 병합 후 `PHYSICS-2`, `PHYSICS-3` 삭제.
- **AREUM**: `AREUM-3` 데이터를 `AREUM-1`으로 이관 후 `AREUM-3`, `AREUM-FORAGER-1` 삭제.

### 2.2 레지스트리 논리적 통합 (Location: Supabase)
- `ba537759-f607-4eda-841c-eeba65a5147b`를 `STRATUM-1`의 유일한 **ACTIVE** 여왕으로 공표.
- 나머지 모든 60여 개의 중복 여왕 레코드는 `CONSOLIDATED_MERGED` 상태로 전환.

### 2.3 환경 및 정찰 고정 (Location: .env)
- 통합된 각 영토의 `.env` 내 `QUEEN_ID`를 위 Primary ID로 고정하여 통신 무결성 100% 보장.

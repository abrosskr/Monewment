# Admin Dashboard Resource Inventory

관리자 페이지(`/admin`)의 모든 리소스 요소를 분석한 결과입니다.

## 📊 데이터 구조 (Interfaces)

### Cluster
- **id**: `number` - 클러스터 고유 식별자
- **name**: `string` - 클러스터 이름
- **region**: `string` - 리전 (예: "kr-seoul-1")
- **status**: `string` - 상태 (ACTIVE, MAINTENANCE, DOWN)
- **organizations**: `Organization[]` - 소속 조직 목록

### Organization
- **id**: `number` - 조직 고유 식별자
- **name**: `string` - 조직 이름
- **status**: `string` - 상태 (PENDING, ACTIVE, SUSPENDED)
- **projects**: `Project[]` - 소속 프로젝트 목록
- **quota**: `{ cpu: number; ram: number; gpu: number }` - 할당된 자원 쿼타

### Project
- **id**: `number` - 프로젝트 고유 식별자
- **name**: `string` - 프로젝트 이름
- **status**: `string` - 상태 (ACTIVE, PENDING, SUSPENDED)

---

## 🎯 상태 관리 (State Variables)

| 변수명 | 타입 | 용도 | 초기값 |
|--------|------|------|--------|
| `mounted` | `boolean` | 하이드레이션 완료 여부 | `false` |
| `hierarchy` | `Cluster[]` | 전체 클러스터 계층 데이터 | `[]` |
| `loading` | `boolean` | 데이터 로딩 상태 | `true` |
| `expandedOrgs` | `number[]` | 펼쳐진 조직 ID 목록 | `[]` |
| `showGuide` | `boolean` | 온보딩 가이드 표시 여부 | `true` |
| `statusMsg` | `string \| null` | 플로팅 토스트 메시지 | `null` |

---

## 🔘 버튼 (Buttons)

### 1. **Status Toast Close Button**
- **위치**: 플로팅 토스트 우측
- **텍스트**: "X"
- **기능**: `setStatusMsg(null)` - 상태 메시지 닫기
- **ID/식별자**: 없음 (className만 존재)
- **클래스**: `ml-4 opacity-50 hover:opacity-100 font-mono`

### 2. **New Cluster Connection**
- **위치**: 헤더 우측 상단
- **텍스트**: "New Cluster Connection"
- **아이콘**: `<PlusCircle size={20} />`
- **기능**: `handleCreateCluster()` - 새 클러스터 생성
- **ID/식별자**: 없음
- **클래스**: `h-14 px-8 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-black uppercase tracking-tighter transition-all flex items-center gap-3 group shadow-[0_0_40px_-10px_rgba(37,99,235,0.6)]`

### 3. **Cluster Activity Button**
- **위치**: 각 클러스터 카드 우측 상단
- **아이콘**: `<Activity size={18} />`
- **기능**: 현재 미구현 (placeholder)
- **ID/식별자**: 없음
- **클래스**: `p-3 bg-white/[0.02] hover:bg-white/[0.05] rounded-2xl text-gray-500 hover:text-white transition-all`

### 4. **Organization Toggle (Expand/Collapse)**
- **위치**: 각 조직 카드 (클릭 가능한 전체 영역)
- **아이콘**: `<ChevronRight />` 또는 `<ChevronDown />`
- **기능**: `toggleOrg(org.id)` - 조직 하위 프로젝트 펼치기/접기
- **ID/식별자**: `key={org.id}`
- **클래스**: `p-6 flex items-center justify-between cursor-pointer`

### 5. **Deploy Project**
- **위치**: 각 조직 카드 우측
- **텍스트**: "Deploy Project"
- **아이콘**: `<FolderPlus size={14} />`
- **기능**: `handleExpandProject(org.id)` - 새 프로젝트 배포
- **ID/식별자**: 없음
- **클래스**: `px-4 py-2 bg-blue-600 text-white border border-blue-400/50 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-500 transition-all shadow-[0_0_20px_-5px_rgba(37,99,235,0.4)] flex items-center gap-2`

### 6. **GOT IT, LET'S COMMAND**
- **위치**: Admin Guide 카드 하단
- **텍스트**: "GOT IT, LET'S COMMAND"
- **기능**: `setShowGuide(false)` - 가이드 닫기
- **ID/식별자**: 없음
- **클래스**: `mt-8 w-full py-4 bg-white text-blue-600 rounded-2xl font-black uppercase text-[10px] tracking-widest hover:bg-blue-50 transition-colors shadow-xl`

### 7. **PROCEED APPROVAL**
- **위치**: Pending Approval 섹션
- **텍스트**: "PROCEED APPROVAL"
- **아이콘**: `<ShieldCheck size={14} />`
- **기능**: `handleApproveOrg(1, hierarchy[0]?.id || 1)` - 조직 승인
- **ID/식별자**: 없음
- **클래스**: `flex-1 py-3 bg-amber-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-amber-500 transition-colors shadow-[0_0_20px_-5px_rgba(245,158,11,0.4)] flex items-center justify-center gap-2`

### 8. **Details**
- **위치**: PROCEED APPROVAL 버튼 옆
- **텍스트**: "Details"
- **기능**: 현재 미구현 (placeholder)
- **ID/식별자**: 없음
- **클래스**: `px-4 py-3 bg-white/5 text-gray-500 rounded-xl text-[10px] font-black hover:bg-white/10 transition-colors`

### 9. **Open Onboarding Guide**
- **위치**: Pending Approval 섹션 하단 (가이드 닫혔을 때만 표시)
- **텍스트**: "Open Onboarding Guide"
- **기능**: `setShowGuide(true)` - 가이드 다시 열기
- **ID/식별자**: 없음
- **조건부 렌더링**: `{!showGuide && (...)}`
- **클래스**: `w-full py-4 border border-dashed border-white/5 rounded-2xl text-[10px] font-black uppercase tracking-widest text-gray-700 hover:text-blue-500 hover:border-blue-500/20 transition-all`

---

## 📝 텍스트 디스플레이 (Text Displays)

### 헤더 섹션
- **타이틀**: "Super Admin Engine" (h1)
- **서브타이틀**: "Platform Command & Control"
- **설명**: "전체 리전 클러스터 상태를 모니터링하고..."

### 통계 카드
- **Clusters 카운트**: `{hierarchy.length}`
- **Global Region**: "KR-1" (하드코딩)

### 클러스터 카드
- **클러스터 이름**: `{cluster.name}` (h3)
- **클러스터 상태**: `{cluster.status}` (badge)
- **리전**: `{cluster.region}`

### 조직 카드
- **조직 이름**: `{org.name}` (h4)
- **Active Quota**: 
  - CPU: `C:{org.quota.cpu}`
  - RAM: `R:{org.quota.ram}G`
  - GPU: `G:{org.quota.gpu}`

### 프로젝트 아이템
- **프로젝트 이름**: `{project.name}`
- **노드 ID**: `NODE-{project.id}`

### Platform Vitals
- **Active Utilization**: "42.8%" (하드코딩)
- **Revenue Today**: "$2,410.5" (하드코딩)
- **VM Nodes**: "128" (하드코딩)

---

## 🎨 아이콘 (Icons from lucide-react)

| 아이콘 | 사용 위치 | 크기 |
|--------|-----------|------|
| `Activity` | 클러스터 액션 버튼, 플로팅 토스트, Platform Vitals | 18px, 20px, 24px |
| `PlusCircle` | New Cluster Connection | 20px |
| `Server` | 클러스터 카드 아이콘 | 32px |
| `Globe` | 클러스터 카드 배경 | 160px |
| `Monitor` | 클러스터 리전 표시 | 12px |
| `Cpu` | 클러스터 인프라 표시 | 12px |
| `Layers` | System Hierarchy 라벨 | 14px |
| `ShieldCheck` | 빈 조직 상태, PROCEED APPROVAL, Admin Guide 배경 | 32px, 14px, 120px |
| `ChevronRight/Down` | 조직 펼치기/접기 | 14px |
| `FolderPlus` | Deploy Project | 14px |
| `Box` | 프로젝트 아이템 | 14px |
| `Info` | Admin Guide 타이틀 | 24px |
| `Clock` | Pending Approval 헤더 | 16px |
| `Zap` | Platform Vitals 헤더 | 16px |

---

## 🔄 API 엔드포인트 연동

| 함수명 | 메서드 | 엔드포인트 | 용도 |
|--------|--------|-----------|------|
| `fetchHierarchy()` | GET | `/api/admin/hierarchy` | 전체 계층 구조 조회 (30초마다 자동 갱신) |
| `handleCreateCluster()` | POST | `/api/admin/clusters` | 새 클러스터 생성 |
| `handleApproveOrg()` | POST | `/api/admin/organizations/approve` | 조직 승인 및 쿼타 할당 |
| `handleExpandProject()` | POST | `/api/admin/projects/expand` | 프로젝트 Top-Down 배포 |

---

## 📋 테이블 구조

현재 대시보드에는 전통적인 `<table>` 요소가 없습니다. 대신:
- **계층적 카드 레이아웃** (Cluster → Organization → Project)
- **그리드 레이아웃** (프로젝트 목록: `grid grid-cols-1 md:grid-cols-2`)
- **통계 그리드** (Platform Vitals: `grid grid-cols-2`)

---

## 🎭 조건부 렌더링

| 조건 | 렌더링 내용 |
|------|------------|
| `!mounted` | `null` (하이드레이션 대기) |
| `loading` | 로딩 스피너 ("Initializing Overlord System...") |
| `statusMsg` | 플로팅 토스트 메시지 |
| `showGuide` | Admin Guide 카드 |
| `!showGuide` | "Open Onboarding Guide" 버튼 |
| `cluster.organizations.length === 0` | "No organizations linked" 빈 상태 |
| `expandedOrgs.includes(org.id)` | 프로젝트 목록 표시 |
| `org.projects.length === 0` | "Zero service nodes initialized" 빈 상태 |

---

## 🆔 Key 속성 (React Keys)

- **Cluster 반복**: `key={cluster.id}`
- **Organization 반복**: `key={org.id}`
- **Project 반복**: `key={project.id}`

---

## 📌 참고사항

1. **ID 속성 부재**: 현재 대부분의 요소에 HTML `id` 속성이 명시적으로 할당되어 있지 않습니다.
2. **식별 방법**: React의 `key` 속성과 데이터 모델의 `id` 필드를 통해 요소를 식별합니다.
3. **접근성**: `aria-label`이나 `role` 속성이 현재 구현되어 있지 않아, 향후 개선이 필요할 수 있습니다.
4. **테스트 자동화**: E2E 테스트를 위해서는 `data-testid` 속성 추가를 권장합니다.

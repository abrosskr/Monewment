# Session End 사용 가이드

## 🏁 세션 종료 스크립트

작업을 마치고 종료할 때 자동으로 masterplan과 할 일 목록을 업데이트하는 스크립트입니다.

### 사용 방법

#### 기본 사용
```powershell
.\scripts\session_end.ps1
```

#### 세션 요약과 함께 사용
```powershell
.\scripts\session_end.ps1 -SessionSummary "Admin Dashboard 완성 및 문서화 시스템 구축"
```

### 자동으로 수행되는 작업

1. **미커밋 변경사항 확인**
   - 커밋되지 않은 파일이 있으면 알림
   - 자동 커밋 옵션 제공

2. **세션 활동 수집**
   - 최근 12시간 동안의 커밋 로그 수집
   - 커밋 개수 카운트

3. **task.md 분석**
   - 완료된 작업 개수 계산
   - 전체 진행률 계산

4. **masterplan.md 업데이트**
   - 세션 요약 추가
   - 타임스탬프 기록
   - 최근 커밋 목록 추가

5. **NEXT_ACTIONS.md 생성**
   - 다음 할 일 목록 자동 생성
   - 우선순위별로 분류
   - 체크리스트 형식

6. **자동 커밋 및 푸시**
   - 업데이트된 문서 자동 커밋
   - GitHub에 자동 푸시

### 생성되는 파일

- `docs/masterplan.md` (업데이트)
- `docs/NEXT_ACTIONS.md` (새로 생성)

### 예제 출력

```
🏁 Monewment Session End - Auto Update
============================================================

📊 [1/5] Checking current status...
✅ No uncommitted changes

📝 [2/5] Collecting session activity...
Found 8 commits in this session

✅ [3/5] Updating task.md...
  Progress: 35/41 tasks (85.4%)

📋 [4/5] Updating masterplan.md...
  ✅ masterplan.md updated

📝 [5/5] Generating next actions...
  ✅ NEXT_ACTIONS.md created

💾 Committing session updates...
  ✅ Changes committed and pushed

============================================================
🎉 Session End Complete!
============================================================

Updated files:
  📋 docs/masterplan.md
  🎯 docs/NEXT_ACTIONS.md

Next time you start, check NEXT_ACTIONS.md for your todo list!

👋 See you next time!
```

### 팁

- 작업을 마칠 때마다 실행하면 자동으로 진행 상황이 기록됩니다
- `NEXT_ACTIONS.md`를 다음 작업 시작 시 참고하세요
- `-SessionSummary` 파라미터로 오늘 한 일을 간단히 요약하세요

### 별칭 설정 (선택사항)

PowerShell Profile에 추가:
```powershell
function End-Session {
    param([string]$summary = "작업 세션 완료")
    & "D:\projects\Monewment\scripts\session_end.ps1" -SessionSummary $summary
}

Set-Alias -Name bye -Value End-Session
```

그러면 이렇게 사용 가능:
```powershell
bye "오늘 Admin Dashboard 완성!"
```

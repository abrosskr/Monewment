export default function BuilderLayout({ children }: { children: React.ReactNode }) {
    return (
        // [핵심] 화면 전체를 덮어버리는 '새 창' 모드 강제 적용
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            backgroundColor: '#050505', // 아주 어두운 배경
            zIndex: 2147483647,        // CSS가 허용하는 최대 높이 (무조건 맨 위)
            overflow: 'hidden',        // 스크롤 방지
            margin: 0,
            padding: 0,
            display: 'flex',
            flexDirection: 'column'
        }}>
            {children}
        </div>
    );
}
import ast
import os

def extract_surrounding_context(file_path: str, target_line: int, context_lines: int = 50) -> str:
    """
    [Phase 2: 노이즈 소각기]
    주어진 파일의 특정 라인 넘버를 중심으로, AST 파싱을 통해 
    가장 밀접한 함수/클래스 블록 전체를 추출합니다.
    """
    if not os.path.exists(file_path):
        return f"[오류] 파일을 찾을 수 없습니다: {file_path}"
    
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()
        
    lines = source_code.splitlines()
    
    try:
        tree = ast.parse(source_code)
    except Exception as e:
        # 구문 오류가 있어 AST 파싱 실패 시, 물리적 라인 슬라이싱으로 Fallback
        start = max(0, target_line - context_lines)
        end = min(len(lines), target_line + context_lines)
        return "\n".join(lines[start:end])

    # 대상 라인을 포함하는 가장 작은 함수/클래스 단위(노드)를 찾습니다.
    target_node = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.lineno <= target_line <= node.end_lineno:
                    # 더 타이트하게 감싸는 노드(내부 함수 등)를 우선순위로 갱신
                    if target_node is None or (node.end_lineno - node.lineno < target_node.end_lineno - target_node.lineno):
                        target_node = node
                        
    if target_node:
        start = max(0, target_node.lineno - 1)
        end = min(len(lines), target_node.end_lineno)
        return "\n".join(lines[start:end])
    else:
        # 찾지 못했을 경우 Fallback
        start = max(0, target_line - context_lines)
        end = min(len(lines), target_line + context_lines)
        return "\n".join(lines[start:end])

def find_route_file(base_dir: str, endpoint_path: str) -> tuple[str, int]:
    """
    HTTP URL 경로를 기반으로 로컬 영토의 라우터 코드 파일과 라인 번호를 탐색합니다.
    (예: "/v1/pipeline/report" -> "report" 라우터 정의부 탐색)
    """
    # 엔드포인트의 가장 마지막 식별자를 검색어(Search Term)로 사용
    parts = endpoint_path.strip("/").split("/")
    if not parts:
        return "", 0
    search_term = parts[-1]
    
    for root, _, files in os.walk(base_dir):
        # .eden, .git 등 금지된 디렉토리는 제외 (로컬 소스만 검색)
        if ".git" in root or ".venv" in root or "__pycache__" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            # FastAPI 라우터 데코레이터에서 문자열 매칭 시도
                            if search_term in line and ("@router" in line or "@app" in line):
                                return file_path, i + 1
                except:
                    continue
    return "", 0

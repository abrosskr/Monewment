import ast
import os

class ConfigInspector:
    def inspect(self, root_dir):
        target_file = os.path.join(root_dir, "src", "config.py")
        if not os.path.exists(target_file): return "# No config.py found"
        
        output = ["# ⚙️ Global Variables & Configurations", f"Source: {target_file}", ""]
        
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                # -------------------------------------------------
                # Case 1: 일반 할당 (Variable = Value) - 기존 로직
                # -------------------------------------------------
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        # 대문자 변수(상수) 추출
                        if isinstance(target, ast.Name) and target.id.isupper():
                            val = self._extract_value(node.value)
                            output.append(f"- `{target.id}` = {val}")

                # -------------------------------------------------
                # Case 2: 타입 힌트 할당 (Variable: Type = Value) - [최적화 추가]
                # -------------------------------------------------
                elif isinstance(node, ast.AnnAssign):
                    if isinstance(node.target, ast.Name) and node.target.id.isupper():
                        # 값이 실제로 할당된 경우만 기록 (예: SECRET_KEY: str) 처럼 선언만 한 경우 제외
                        if node.value:
                            val = self._extract_value(node.value)
                            output.append(f"- `{node.target.id}` = {val}")
                            
        except Exception as e:
            output.append(f"Error parsing config: {e}")
            
        return "\n".join(output)

    def _extract_value(self, node_value):
        """AST 노드에서 값을 추출하는 헬퍼 메서드 (중복 제거 및 최적화)"""
        val = "Complex Value" # 기본값

        # 1. 고정값 (문자, 숫자)
        if isinstance(node_value, ast.Constant):
            raw_val = node_value.value
            val = f'"{raw_val}"' if isinstance(raw_val, str) else str(raw_val)
        
        # 2. 함수 호출 감지 (예: os.getenv("KEY"))
        elif isinstance(node_value, ast.Call):
            func_name = "func()"
            # 함수 이름 추출
            if isinstance(node_value.func, ast.Attribute):
                func_name = node_value.func.attr # getenv
            elif isinstance(node_value.func, ast.Name):
                func_name = node_value.func.id
            
            # 인자값 대략적으로 추출
            args = []
            for arg in node_value.args:
                if isinstance(arg, ast.Constant):
                    args.append(f'"{arg.value}"')
                elif isinstance(arg, ast.Name):
                    args.append(arg.id)
            val = f"{func_name}({', '.join(args)})"

        # 3. 다른 변수 참조 (예: BASE_URL = URL)
        elif isinstance(node_value, ast.Name):
            val = f"Ref({node_value.id})"
            
        return val
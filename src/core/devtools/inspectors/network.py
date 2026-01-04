import ast
import os

class NetworkInspector:
    def inspect(self, root_dir):
        # 1. 감시 대상 설정: routers 폴더 + main.py 추가 (최적화)
        routers_dir = os.path.join(root_dir, "src", "routers")
        main_file = os.path.join(root_dir, "src", "main.py")
        
        output = ["# 📡 Communication & API Specification", ""]
        
        # (1) Routers 폴더 스캔 (기존 로직 유지)
        if os.path.exists(routers_dir):
            for f_name in os.listdir(routers_dir):
                if f_name.endswith(".py") and f_name != "__init__.py":
                    path = os.path.join(routers_dir, f_name)
                    output.append(self._analyze_file(path, f"Router: `{f_name}`"))

        # (2) Main.py 스캔 (신규 추가: 핵심 API 누락 방지)
        if os.path.exists(main_file):
            output.append(self._analyze_file(main_file, "Core: `main.py`"))
            
        return "\n".join(output)

    def _analyze_file(self, file_path, title):
        """파일 단위 분석 로직 (중복 제거 및 최적화)"""
        results = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
                
            found_apis = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for dec in node.decorator_list:
                        # 데코레이터 분석 (Call: @app.get(...))
                        if isinstance(dec, ast.Call):
                            method = ""
                            url = "Unknown"
                            
                            # HTTP 메서드 추출 (@router.get, @app.post 등)
                            if isinstance(dec.func, ast.Attribute):
                                method = dec.func.attr.upper()
                            
                            # 유효한 HTTP 메서드인 경우만 기록
                            if method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                                # URL 추출
                                if dec.args and hasattr(dec.args[0], 'value'):
                                    url = dec.args[0].value
                                
                                # [최적화 추가] 한글 주석(Docstring) 추출
                                # 함수 바로 아래의 """주석"""을 읽어옵니다.
                                docstring = ast.get_docstring(node) or "설명 없음"
                                description = docstring.split('\n')[0].strip() # 첫 줄만 추출

                                # 파라미터(Protocol) 분석
                                params = [a.arg for a in node.args.args if a.arg != "self"]
                                param_str = ", ".join(params) if params else "(No params)"
                                
                                found_apis.append(f"- `[{method}]` **{url}**")
                                found_apis.append(f"  - **기능: {description}**") # 한글 기능 설명 추가
                                found_apis.append(f"  - Handler: `{node.name}`")
                                found_apis.append(f"  - Params (Protocol): {param_str}")

            if found_apis:
                results.append(f"\n## 📄 {title}")
                results.extend(found_apis)
                
        except Exception as e:
            results.append(f"\n## ⚠️ Error analyzing {os.path.basename(file_path)}: {e}")
            
        return "\n".join(results)
import ast
import os

class DatabaseInspector:
    def inspect(self, root_dir):
        target_file = os.path.join(root_dir, "src", "models.py")
        if not os.path.exists(target_file): return "# No models.py found"
        
        output = ["# 📊 Data & DB Schema (Table Blueprint)", f"Source: {target_file}", ""]
        
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Base를 상속받는 클래스만 테이블로 간주
                    is_table = any(b.id == 'Base' for b in node.bases if isinstance(b, ast.Name))
                    
                    if is_table:
                        output.append(f"\n## 🧱 Table: `{node.name}`")
                        output.append("- Columns:")
                        
                        # 컬럼 분석
                        for item in node.body:
                            # id = Column(Integer, ...) 형태 파싱
                            if isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        col_name = target.id
                                        col_type = "(Defined Value)"
                                        
                                        # 값 부분 분석 (Column 호출인지 확인)
                                        if isinstance(item.value, ast.Call) and hasattr(item.value.func, 'id'):
                                            if item.value.func.id == 'Column':
                                                # Column의 첫 번째 인자가 타입임 (Integer, String 등)
                                                if item.value.args:
                                                    first_arg = item.value.args[0]
                                                    if isinstance(first_arg, ast.Name):
                                                        col_type = first_arg.id
                                                    elif isinstance(first_arg, ast.Call): # DateTime(timezone=True)
                                                        if hasattr(first_arg.func, 'id'):
                                                            col_type = first_arg.func.id
                                                else:
                                                    col_type = "Unknown"
                                        
                                        # Relationship 등은 건너뛰거나 별도 표기 가능하지만 여기선 Column만 집중
                                        if "relationship" not in str(item.value):
                                            output.append(f"  - `{col_name}` : **{col_type}**")
                                            
        except Exception as e:
            return f"Error analyzing DB: {e}"
            
        return "\n".join(output)

    def _get_type_name(self, node):
        # (SQLModel용 레거시 헬퍼 - 혹시 몰라 남겨둠)
        if isinstance(node, ast.Name): return node.id
        return "ComplexType"
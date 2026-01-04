import os

class StructureInspector:
    def inspect(self, root_dir):
        exclude = {'.git', '.next', 'node_modules', '__pycache__', '.vscode', 'venv', '.idea', 'dist', 'build'}
        tree = ["# 📂 Project Structure Map", ""]
        
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude]
            level = root.replace(root_dir, '').count(os.sep)
            indent = '│   ' * level
            
            folder_name = os.path.basename(root)
            if folder_name == os.path.basename(root_dir):
                tree.append(f"📦 {folder_name}")
            else:
                tree.append(f"{indent}📂 {folder_name}/")
            
            for f in files:
                if f.startswith('.'): continue
                tree.append(f"{indent}│   📄 {f}")
                
        return "\n".join(tree)

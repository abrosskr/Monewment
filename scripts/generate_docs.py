# scripts/generate_docs.py
import os

def generate_tree(startpath, output_file):
    """
    프로젝트 폴더 구조를 스캔하여 Markdown 트리 형태로 저장합니다.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 🏗️ Project Structure\n\n")
        f.write("```text\n")
        
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            indent = '│   ' * (level)
            
            # 숨김 폴더/파일 제외
            if '.git' in root or '__pycache__' in root or '.venv' in root:
                continue
                
            subindent = '├── '
            f.write(f'{indent}{subindent}{os.path.basename(root)}/\n')
            
            for i, file in enumerate(files):
                if file.startswith('.') or file.endswith('.pyc'):
                    continue
                if i == len(files) - 1:
                    sub_subindent = '└── '
                else:
                    sub_subindent = '├── '
                f.write(f'{indent}│   {sub_subindent}{file}\n')
                
        f.write("```\n")
        f.write("\n> Last Updated: By Monewment Auto-Doc Script\n")

if __name__ == "__main__":
    # 프로젝트 루트 경로 (스크립트 상위 폴더)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(root_dir, "docs", "STRUCTURE.md")
    
    # docs 폴더 없으면 생성
    os.makedirs(os.path.join(root_dir, "docs"), exist_ok=True)
    
    print(f"🔍 Scanning project: {root_dir}")
    generate_tree(root_dir, output_path)
    print(f"✅ Documentation generated at: {output_path}")
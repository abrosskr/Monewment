# scripts/generate_docs.py
import os
import requests # [추가] AI 분석 통신용
import json
from datetime import datetime

def generate_tree(startpath, output_file):
    """
    해선님 원본 로직 100% 유지: 프로젝트 폴더 구조를 스캔하여 Markdown 트리 형태로 저장합니다.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 🏗️ Project Structure (Monewment 자율 생성 문서)\n\n")
        f.write("```text\n")
        
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            indent = '│   ' * (level)
            
            if '.git' in root or '__pycache__' in root or '.venv' in root or 'node_modules' in root:
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

# [최적화 추가] 프로젝트의 설계 의도와 히스토리를 분석하는 AI 기능입니다.
def analyze_intent_with_ai():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "\n> ⚠️ Gemini API 키가 설정되지 않아 AI 분석을 건너뜁니다."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # AI에게 줄 컨텍스트입니다.
    prompt = "현재 프로젝트의 파일 구조와 코드를 바탕으로 이 프로젝트의 '설계 의도'와 '주요 기능'을 상세히 분석하여 Markdown 형식으로 요약해줘."
    
    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return f"\n## 🧠 AI 프로젝트 분석 보고서\n\n{response.json()['candidates'][0]['content']['parts'][0]['text']}"
    except:
        pass
    return "\n> ❌ AI 분석 중 오류가 발생했습니다."

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(root_dir, "docs", "STRUCTURE.md")
    
    os.makedirs(os.path.join(root_dir, "docs"), exist_ok=True)
    
    print(f"🔍 Scanning project: {root_dir}")
    # 1. 원본 트리 생성
    generate_tree(root_dir, output_path)
    
    # 2. AI 분석 내용 추가
    analysis_result = analyze_intent_with_ai()
    with open(output_path, 'a', encoding='utf-8') as f:
        f.write(analysis_result)
        f.write(f"\n\n--- \n> Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | By Monewment Auto-Doc Script\n")
        
    print(f"✅ Documentation generated at: {output_path}")
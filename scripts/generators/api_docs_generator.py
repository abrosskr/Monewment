"""
API 문서 생성기 (Enhanced Version)
FastAPI 소스 코드를 직접 스캔하여 완전한 API 레퍼런스를 생성합니다.
"""

import os
import re
import ast
from datetime import datetime
from typing import List, Dict, Any

def scan_fastapi_routes(root_dir: str) -> List[Dict[str, Any]]:
    """FastAPI 라우트를 소스 코드에서 직접 스캔"""
    
    main_py = os.path.join(root_dir, "src", "main.py")
    if not os.path.exists(main_py):
        return []
    
    routes = []
    
    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # @app.get, @app.post 등의 데코레이터 패턴 찾기
    route_pattern = r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)'
    
    for match in re.finditer(route_pattern, content):
        method = match.group(1).upper()
        path = match.group(2)
        
        # 함수 이름 및 docstring 추출
        func_start = match.end()
        func_match = re.search(r'def\s+(\w+)\s*\(', content[func_start:func_start+200])
        
        if func_match:
            func_name = func_match.group(1)
            
            # Docstring 추출
            docstring_match = re.search(
                r'def\s+' + func_name + r'\s*\([^)]*\):\s*"""([^"]+)"""',
                content[func_start:func_start+500]
            )
            
            description = docstring_match.group(1).strip() if docstring_match else func_name.replace('_', ' ').title()
            
            # 태그 추론 (경로 기반)
            tag = "General"
            if "/auth/" in path:
                tag = "Authentication"
            elif "/admin/" in path:
                tag = "Admin"
            elif "/api/vms" in path:
                tag = "Virtual Machines"
            elif "/api/projects" in path:
                tag = "Projects"
            elif "/api/organizations" in path:
                tag = "Organizations"
            elif "/api/clusters" in path:
                tag = "Clusters"
            
            routes.append({
                "method": method,
                "path": path,
                "name": func_name,
                "description": description,
                "tag": tag
            })
    
    return routes

def generate_api_docs(root_dir, output_dir):
    """API 레퍼런스 문서 생성"""
    
    # API 엔드포인트 스캔
    api_list = scan_fastapi_routes(root_dir)
    
    # 문서 작성
    output_file = os.path.join(output_dir, "API_REFERENCE.md")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 📡 Monewment API Reference\n\n")
        f.write(f"> **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
        f.write("> **Base URL:** `http://localhost:8001`\\n\\n")
        f.write(f"> **Total Endpoints:** {len(api_list)}\\n\\n")
        
        f.write("---\\n\\n")
        
        # 인증 섹션
        f.write("## 🔐 Authentication\\n\\n")
        f.write("Most endpoints require JWT authentication. Include the token in the Authorization header:\\n\\n")
        f.write("```http\\n")
        f.write("Authorization: Bearer <your_jwt_token>\\n")
        f.write("```\\n\\n")
        
        f.write("### Obtaining a Token\\n\\n")
        f.write("```http\\n")
        f.write("POST /api/auth/login\\n")
        f.write("Content-Type: application/json\\n\\n")
        f.write("{\\n")
        f.write('  "email": "user@example.com",\\n')
        f.write('  "password": "your_password"\\n')
        f.write("}\\n")
        f.write("```\\n\\n")
        
        f.write("---\\n\\n")
        
        # 태그별로 그룹화
        grouped_apis = {}
        for api in api_list:
            tag = api.get('tag', 'General')
            
            if tag not in grouped_apis:
                grouped_apis[tag] = []
            grouped_apis[tag].append(api)
        
        # 각 태그별로 문서 작성
        for tag, apis in sorted(grouped_apis.items()):
            f.write(f"## 📂 {tag}\\n\\n")
            
            for api in apis:
                path = api.get('path', '/unknown')
                method = api.get('method', 'GET')
                name = api.get('name', 'Unknown')
                description = api.get('description', '설명 없음')
                
                f.write(f"### `{method} {path}`\\n\\n")
                f.write(f"**Description:** {description}\\n\\n")
                f.write(f"**Function:** `{name}()`\\n\\n")
                
                # 요청 예제
                f.write("**Request Example:**\\n\\n")
                f.write("```http\\n")
                f.write(f"{method} {path} HTTP/1.1\\n")
                f.write("Host: localhost:8001\\n")
                
                if method in ['POST', 'PUT', 'PATCH']:
                    f.write("Content-Type: application/json\\n")
                    if tag != "Authentication":
                        f.write("Authorization: Bearer <token>\\n")
                    f.write("\\n")
                    f.write(generate_request_body(path, method))
                elif tag != "Authentication":
                    f.write("Authorization: Bearer <token>\\n")
                
                f.write("```\\n\\n")
                
                # 응답 예제
                f.write("**Response Example:**\\n\\n")
                f.write("```json\\n")
                f.write(generate_response_example(path, method))
                f.write("```\\n\\n")
                
                f.write("---\\n\\n")
        
        # 에러 코드 섹션
        f.write("## ⚠️ Error Codes\\n\\n")
        f.write("| Code | Description |\\n")
        f.write("|------|-------------|\\n")
        f.write("| 200 | Success |\\n")
        f.write("| 201 | Created |\\n")
        f.write("| 400 | Bad Request |\\n")
        f.write("| 401 | Unauthorized |\\n")
        f.write("| 403 | Forbidden |\\n")
        f.write("| 404 | Not Found |\\n")
        f.write("| 500 | Internal Server Error |\\n\\n")
        
        f.write("---\\n\\n")
        f.write("*Generated by Monewment Auto-Doc System v4.0*\\n")
    
    return {
        'file': output_file,
        'endpoints_count': len(api_list)
    }

def generate_request_body(path, method):
    """경로에 따른 요청 본문 예제 생성"""
    
    if 'login' in path.lower():
        return '''{
  "email": "admin@example.com",
  "password": "secure_password"
}'''
    elif 'signup' in path.lower():
        return '''{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "User Name"
}'''
    elif 'cluster' in path.lower() and method == 'POST':
        return '''{
  "name": "Seoul-Cluster-1",
  "region": "kr-seoul-1",
  "cpu_capacity": 1000,
  "ram_capacity_gb": 4096,
  "gpu_capacity": 64
}'''
    elif 'approve' in path.lower():
        return '''{
  "org_id": 1,
  "cluster_id": 1,
  "quota_cpu": 20,
  "quota_ram_gb": 64,
  "quota_gpu": 2
}'''
    elif 'project' in path.lower() and 'expand' in path.lower():
        return '''{
  "org_id": 1,
  "project_name": "MyProject"
}'''
    elif '/api/vms' in path and method == 'POST':
        return '''{
  "project_id": 1,
  "flavor_id": 1,
  "name": "my-vm-instance"
}'''
    else:
        return '{}'

def generate_response_example(path, method):
    """경로에 따른 응답 예제 생성"""
    
    if 'login' in path.lower():
        return '''{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "role": "ADMIN"
  }
}'''
    elif 'hierarchy' in path.lower():
        return '''{
  "hierarchy": [
    {
      "id": 1,
      "name": "Seoul-Cluster-1",
      "region": "kr-seoul-1",
      "status": "ACTIVE",
      "organizations": [
        {
          "id": 1,
          "name": "Example Corp",
          "quota_cpu": 20,
          "quota_ram_gb": 64,
          "quota_gpu": 2,
          "projects": [...]
        }
      ]
    }
  ]
}'''
    elif 'cluster' in path.lower() and method == 'POST':
        return '''{
  "message": "Cluster created successfully",
  "cluster": {
    "id": 1,
    "name": "Seoul-Cluster-1",
    "region": "kr-seoul-1",
    "status": "ACTIVE"
  }
}'''
    elif method == 'DELETE':
        return '''{
  "message": "Successfully deleted",
  "id": 1
}'''
    elif '/api/vms' in path:
        return '''{
  "id": 1,
  "name": "my-vm-instance",
  "status": "RUNNING",
  "flavor": {
    "cpu_cores": 4,
    "memory_gb": 16,
    "gpu_model": "RTX 4090"
  }
}'''
    else:
        return '''{
  "message": "Success",
  "data": {}
}'''

if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output = os.path.join(root, "docs", "auto_generated")
    os.makedirs(output, exist_ok=True)
    
    result = generate_api_docs(root, output)
    print(f"✅ API 문서 생성 완료: {result}")

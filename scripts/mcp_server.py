import os
import uvicorn
import psycopg2
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# 1. 환경 설정
load_dotenv()

# MCP 서버 정의 (FastAPI 기반)
mcp = FastMCP("Vendors K8s Server")

# K8s 내부에서는 'localhost'가 아니라 DB 서비스 이름을 씁니다.
# 로컬 테스트할 때는 .env 파일이 우선하므로 걱정 없습니다.
DB_HOST = os.getenv("DB_HOST", "db-service")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "yourpassword") # 실제론 K8s Secret 사용 권장
DB_NAME = os.getenv("DB_NAME", "postgres")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )

# ... (Tool 1: 파일 시스템 - 기존과 동일) ...
@mcp.tool()
def list_directory(path: str = ".") -> str:
    """프로젝트 폴더 내의 파일 목록을 조회합니다."""
    try:
        if not os.path.exists(path): return "Error: 경로 없음"
        items = [i for i in os.listdir(path) if i not in ['.git', '__pycache__', 'node_modules']]
        return "\n".join(items)
    except Exception as e: return str(e)

@mcp.tool()
def read_file(file_path: str) -> str:
    """파일 내용을 읽습니다."""
    try:
        if not os.path.exists(file_path): return "Error: 파일 없음"
        with open(file_path, "r", encoding="utf-8") as f: return f.read()
    except Exception as e: return str(e)

# ... (Tool 2: 데이터베이스 - 기존과 동일) ...
@mcp.tool()
def get_db_tables() -> str:
    """DB 테이블 목록 조회"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [row[0] for row in cur.fetchall()]
        conn.close()
        return f"Tables: {', '.join(tables)}"
    except Exception as e: return f"DB Error: {str(e)}"

@mcp.tool()
def get_db_schema(table_name: str) -> str:
    """테이블 스키마 조회"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'")
        rows = cur.fetchall()
        conn.close()
        return "\n".join([f"- {r[0]}: {r[1]}" for r in rows])
    except Exception as e: return f"DB Error: {str(e)}"

# [핵심 변경] stdio 대신 uvicorn 웹 서버 실행
if __name__ == "__main__":
    print("🚀 Vendors MCP Server starting in Network Mode (SSE)...")
    # 0.0.0.0으로 열어야 K8s 외부에서 접속 가능
    mcp.run(transport="sse")
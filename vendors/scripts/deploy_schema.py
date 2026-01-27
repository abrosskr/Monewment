
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load env variables
load_dotenv(".env.local")

def deploy_schema(target_env="BRAIN"):
    """
    Deploys the schema to the specified Supabase project.
    target_env: "BRAIN" or "LIVE"
    """
    print(f"🚀 Deploying Schema to {target_env}...")
    
    # Supabase provides a direct Postgres connection string.
    # Format: postgres://postgres:[PASSWORD]@[HOST]:6543/postgres
    # We need to ask the user for this, as it's NOT the API URL.
    
    db_url = os.getenv(f"SUPABASE_{target_env}_DB_URL")
    if not db_url:
        print(f"❌ Error: SUPABASE_{target_env}_DB_URL is missing in .env.local")
        print(f"Please add the connection string from Supabase Dashboard -> Settings -> Database -> Connection String")
        return

    schema_file = "supabase_schema_full.sql"
    
    try:
        print(f"📡 Connecting to Database...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        with open(schema_file, "r", encoding="utf-8") as f:
            sql_content = f.read()
            
        print(f"📜 Executing SQL from {schema_file}...")
        cur.execute(sql_content)
        conn.commit()
        
        print("✅ Schema deployed successfully!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Deployment Failed: {e}")

if __name__ == "__main__":
    print("Select Target to Deploy:")
    print("1. Brain (Lab)")
    print("2. Live (Restaurant)")
    choice = input("Enter 1 or 2: ")
    
    if choice == "1":
        deploy_schema("BRAIN")
    elif choice == "2":
        deploy_schema("LIVE")
    else:
        print("Invalid choice")

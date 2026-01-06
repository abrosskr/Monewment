
import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.database import SessionLocal
from src.models import User
from src.core.security import hash_password

def migrate_passwords():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        migrated_count = 0
        
        print(f"[*] Found {len(users)} users to check.")
        
        for user in users:
            # Bcrypt hashes usually start with $2b$ or $2a$
            if not user.hashed_password.startswith("$2b$"):
                print(f"[!] Hashing plaintext password for user: {user.email}")
                user.hashed_password = hash_password(user.hashed_password)
                migrated_count += 1
        
        db.commit()
        print(f"[+] Migration complete. {migrated_count} users updated.")
        
    except Exception as e:
        print(f"[-] Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_passwords()

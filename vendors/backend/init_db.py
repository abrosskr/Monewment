import sys
import os
sys.path.append(os.getcwd())

from app.database import engine, Base
from app.models.recipe import ScrapedRecipe
# Import other models if needed to ensure they are registered
from app.models.fis_protocol import FisFile

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import create_engine
from src.app.database import Base
# Import models to ensure they are registered on Base
from src.app import models

def test_models_creation():
    print("Testing SQLAlchemy models creation on an in-memory SQLite database...")
    # Using sqlite in-memory database to verify schema definition correctness
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        print("Success! All models (User, Profile, UserSettings, Application, JobFound, CustomCoverLetter, EmailInteraction) created successfully in SQLite.")
    except Exception as e:
        print(f"Failed to create tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_models_creation()

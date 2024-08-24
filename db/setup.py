# db/setup.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL
from db.models import Base


def setup_database():
    # Extract the database file path from the DATABASE_URL (assuming SQLite)
    db_path = DATABASE_URL.split('///')[-1]

    # Check if the database file already exists
    if not os.path.exists(db_path):
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(engine)
        print("Database setup complete.")
    else:
        print("Database already initialized. Skipping setup.")

if __name__ == '__main__':
    setup_database()

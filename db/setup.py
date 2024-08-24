# db/setup.py
from sqlalchemy import create_engine
from config.settings import DATABASE_URL
from db.models import Base

def setup_database():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Database has been set up.")

if __name__ == '__main__':
    setup_database()

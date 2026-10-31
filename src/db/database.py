import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from src.db.models import Base

def get_engine():
    """Create the database engine from DATABASE_URL."""
    load_dotenv()
    return create_engine(os.environ["DATABASE_URL"])

def init_db(engine):
    """Create the tables if they do not exist."""
    Base.metadata.create_all(engine)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

Base = declarative_base()

def init_db(app):
    # Create engine
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    engine = create_engine(database_url)
    
    # Create session factory
    session_factory = sessionmaker(bind=engine)
    
    # Create tables
    Base.metadata.create_all(engine)
    
    return session_factory

# Function to get a new session
def get_session(app):
    session_factory = init_db(app)
    return session_factory()
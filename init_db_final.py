from main import create_app
from utils.db import db
app = create_app()

def create_tables_with_dependencies():
    # Completely drop all existing tables first
    from sqlalchemy import text
    db.session.execute(text("DROP TABLE IF EXISTS journey_steps"))
    db.session.execute(text("DROP TABLE IF EXISTS legal_journeys"))
    db.session.execute(text("DROP TABLE IF EXISTS cases"))
    db.session.execute(text("DROP TABLE IF EXISTS form_templates"))
    db.session.execute(text("DROP TABLE IF EXISTS users"))
    
    # Create tables in strict dependency order
    db.session.execute(text("""
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """))
    
    db.session.execute(text("""
    CREATE TABLE form_templates (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        form_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """))
    
    db.session.execute(text("""
    CREATE TABLE cases (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """))
    
    db.session.execute(text("""
    CREATE TABLE legal_journeys (
        id SERIAL PRIMARY KEY,
        case_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (case_id) REFERENCES cases (id)
    )
    """))
    
    db.session.execute(text("""
    CREATE TABLE journey_steps (
        id SERIAL PRIMARY KEY,
        journey_id INTEGER NOT NULL,
        step_title TEXT NOT NULL,
        step_description TEXT,
        form_template_id INTEGER,
        FOREIGN KEY (journey_id) REFERENCES legal_journeys (id),
        FOREIGN KEY (form_template_id) REFERENCES form_templates (id)
    )
    """))
    
    # Commit all changes
    db.session.commit()

with app.app_context():
    print("Creating database tables with enforced dependency order...")
    create_tables_with_dependencies()
    print("Database tables created successfully with all foreign keys!")
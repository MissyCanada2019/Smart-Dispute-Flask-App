from main import create_app
from utils.db import db
app = create_app()

def create_tables_in_order():
    # Create independent tables first
    db.session.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    db.session.execute("""
    CREATE TABLE IF NOT EXISTS form_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        form_data TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    db.session.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'open',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Create dependent tables
    db.session.execute("""
    CREATE TABLE IF NOT EXISTS legal_journeys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (case_id) REFERENCES cases (id)
    )
    """)
    
    db.session.execute("""
    CREATE TABLE IF NOT EXISTS journey_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        journey_id INTEGER NOT NULL,
        step_title TEXT NOT NULL,
        step_description TEXT,
        form_template_id INTEGER,
        FOREIGN KEY (journey_id) REFERENCES legal_journeys (id),
        FOREIGN KEY (form_template_id) REFERENCES form_templates (id)
    )
    """)
    
    # Commit all changes
    db.session.commit()

with app.app_context():
    print("Creating database tables with proper dependency order...")
    create_tables_in_order()
    print("Database tables created successfully!")
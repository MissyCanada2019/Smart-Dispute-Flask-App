from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def init_db(app):
    # Configure database URI
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    # Initialize SQLAlchemy with app
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
        
    return db
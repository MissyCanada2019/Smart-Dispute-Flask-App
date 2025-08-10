#!/usr/bin/env python3
"""
Proper Database Initialization Script for Smart Dispute Canada
This script initializes the database with the correct schema based on the models.
"""

from main import create_app
from utils.db import db
from models.user import User
from models.case import Case
from models.evidence import Evidence
from models.court_form import CourtForm, FormField, FormSubmission
from models.legal_journey import LegalJourney, JourneyStep
from models.notification import Notification
import os

def init_database():
    """Initialize database with tables and default data"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Initializing Smart Dispute Canada database...")
        
        # Create all tables based on models
        print("📋 Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@smartdispute.ca').first()
        if not admin_user:
            print("👤 Creating admin user...")
            admin_user = User(
                email='admin@smartdispute.ca',
                is_admin=True,
                is_active=True
            )
            admin_user.set_password('admin123')  # Change this password!
            db.session.add(admin_user)
            print("✅ Admin user created successfully")
        else:
            print("ℹ️  Admin user already exists")
        
        # Check if test user already exists
        test_user = User.query.filter_by(email='test@smartdispute.ca').first()
        if not test_user:
            print("👤 Creating test user...")
            test_user = User(
                email='test@smartdispute.ca',
                is_admin=False,
                is_active=True
            )
            test_user.set_password('test123')  # Change this password!
            db.session.add(test_user)
            print("✅ Test user created successfully")
        else:
            print("ℹ️  Test user already exists")
        
        # Commit changes
        db.session.commit()
        
        print("\n🎉 Database initialization complete!")
        print("\n📋 Login Credentials:")
        print("   👑 Admin: admin@smartdispute.ca / admin123")
        print("   👤 Test User: test@smartdispute.ca / test123")
        print("\n🚨 IMPORTANT: Change these passwords immediately after first login!")

if __name__ == '__main__':
    init_database()
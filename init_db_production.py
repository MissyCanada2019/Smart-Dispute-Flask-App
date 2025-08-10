#!/usr/bin/env python3
"""
Production Database Initialization Script for Smart Dispute Canada
This script initializes the database with the correct schema based on the models
and seeds it with initial data for production deployment.
"""

import os
import sys
from main import create_app
from utils.db import db
from models.user import User
from models.case import Case
from models.evidence import Evidence
from models.court_form import CourtForm, FormField, FormSubmission
from models.legal_journey import LegalJourney, JourneyStep
from models.notification import Notification

def init_production_database():
    """Initialize production database with tables and default data"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Initializing Smart Dispute Canada production database...")
        
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
            # In production, you should change this password immediately after first login
            admin_user.set_password('ChangeMeImmediately2024!')
            db.session.add(admin_user)
            print("✅ Admin user created successfully")
        else:
            print("ℹ️  Admin user already exists")
        
        # Commit changes
        db.session.commit()
        
        print("\n🎉 Production database initialization complete!")
        print("\n📋 Login Credentials:")
        print("   👑 Admin: admin@smartdispute.ca / ChangeMeImmediately2024!")
        print("\n🚨 IMPORTANT: Change the admin password immediately after first login!")
        print("\n📝 Next steps:")
        print("   1. Log in as admin@smartdispute.ca with the password above")
        print("   2. Go to the admin panel to change your password")
        print("   3. Add additional users as needed")
        print("   4. Configure any additional settings in the admin panel")

if __name__ == '__main__':
    init_production_database()
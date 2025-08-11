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

import secrets
import string

def generate_secure_password(length=16):
    """Generates a secure, random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for i in range(length))

def init_production_database():
    """Initialize production database with tables and default data"""
    app = create_app()
    
    with app.app_context():
        print("Initializing Smart Dispute Canada production database...")
        
        # Create all tables based on models
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully")
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@smartdispute.ca').first()
        if not admin_user:
            print("Creating admin user...")
            admin_user = User(
                email='admin@smartdispute.ca',
                is_admin=True,
                is_active=True
            )
            # Generate a secure, random password for the admin user
            admin_password = generate_secure_password()
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created successfully.")
            print("\n" + "="*50)
            print("🚨 IMPORTANT: SECURE ADMIN PASSWORD GENERATED 🚨")
            print("="*50)
            print("Please save the following admin credentials in a secure location.")
            print("This password will only be displayed once.")
            print(f"  => Email:    admin@smartdispute.ca")
            print(f"  => Password: {admin_password}")
            print("="*50 + "\n")
        else:
            print("ℹ️ Admin user already exists. Password not changed.")
        print("\nProduction database initialization complete!")
        print("\n📝 Next steps:")
        print("   1. Log in as admin@smartdispute.ca with the password above")
        print("   2. Go to the admin panel to change your password")
        print("   3. Add additional users as needed")
        print("   4. Configure any additional settings in the admin panel")

if __name__ == '__main__':
    init_production_database()
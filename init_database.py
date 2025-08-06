#!/usr/bin/env python3
"""
Database Initialization Script for Smart Dispute Canada
Run this to fix the client-side error after deployment
"""

from main import create_app
from utils.db import db
from models.user import User
from models.court_form import CourtForm
from utils.form_templates import FormTemplateManager
import os

def init_database():
    """Initialize database with tables and default data"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Initializing Smart Dispute Canada database...")
        
        # Drop and recreate all tables
        print("📋 Creating database tables...")
        db.drop_all()
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Create admin user
        print("👤 Creating admin user...")
        admin_user = User(
            email='admin@smartdispute.ca',
            is_admin=True,
            is_active=True
        )
        admin_user.set_password('admin123')  # Change this password!
        db.session.add(admin_user)
        
        # Create test user
        print("👤 Creating test user...")
        test_user = User(
            email='test@smartdispute.ca',
            is_admin=False,
            is_active=True
        )
        test_user.set_password('test123')  # Change this password!
        db.session.add(test_user)
        
        db.session.commit()
        print("✅ Users created successfully")
        
        # Initialize form templates
        print("📝 Initializing court form templates...")
        try:
            template_manager = FormTemplateManager()
            created_count = template_manager.initialize_default_templates()
            print(f"✅ Created {created_count} form templates")
        except Exception as e:
            print(f"⚠️  Form template initialization failed: {str(e)}")
            print("   (This is not critical - forms can be added later)")
        
        print("\n🎉 Database initialization complete!")
        print("\n📋 Login Credentials:")
        print("   👑 Admin: admin@smartdispute.ca / admin123")
        print("   👤 Test User: test@smartdispute.ca / test123")
        print("\n🚨 IMPORTANT: Change these passwords immediately after first login!")
        
if __name__ == '__main__':
    init_database()
#!/usr/bin/env python3
"""
Test script to verify that the Smart Dispute Canada application can start
and connect to the database without errors.
"""

import os
import sys
from main import create_app
from utils.db import db
from models.user import User

def test_application():
    """Test the application startup and database connection"""
    print("🔧 Testing Smart Dispute Canada application...")
    
    try:
        # Create the application
        app = create_app()
        
        with app.app_context():
            print("✅ Application created successfully")
            
            # Test database connection
            print("📋 Testing database connection...")
            db.session.execute(db.text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Test database query
            print("📋 Testing database query...")
            user_count = User.query.count()
            print(f"✅ Database query successful - Found {user_count} users")
            
            # Test health check
            print("📋 Testing health check...")
            from utils.error_handling import HealthCheck
            health_status = HealthCheck.get_health_status()
            if health_status['status'] == 'healthy':
                print("✅ Health check passed")
            else:
                print(f"⚠️  Health check failed: {health_status}")
                
        print("\n🎉 All tests passed! The application is ready for deployment.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_application()
    sys.exit(0 if success else 1)
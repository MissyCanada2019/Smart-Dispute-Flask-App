#!/usr/bin/env python3
"""
Test script for the enhanced health check functionality
"""

import sys
import os

# Add the current directory to the Python path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up a basic Flask application context for testing
from flask import Flask
from utils.db import db

# Create a minimal Flask app for testing
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

# Initialize the database
db.init_app(app)

# Import the HealthCheck class
from utils.error_handling import HealthCheck

def test_health_check():
    """Test the enhanced health check functionality"""
    with app.app_context():
        print("Running enhanced health check...")
        health_status = HealthCheck.get_health_status()
        
        print(f"Overall status: {health_status['status']}")
        print(f"Timestamp: {health_status['timestamp']}")
        print("\nDetailed checks:")
        
        for check_name, check_result in health_status['checks'].items():
            status = "✓" if check_result['status'] == 'ok' else "✗"
            print(f"  {status} {check_name}: {check_result['message']}")
        
        return health_status

if __name__ == "__main__":
    test_health_check()
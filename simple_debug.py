#!/usr/bin/env python3
"""
Simple debug script for the enhanced health check functionality
"""

import sys
import os

# Add the current directory to the Python path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import the required modules and handle import errors
try:
    import psutil
    print("✅ psutil imported successfully")
except ImportError as e:
    print(f"❌ psutil import failed: {e}")
    psutil = None

try:
    from flask import Flask
    print("✅ Flask imported successfully")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    sys.exit(1)

try:
    from utils.db import db
    print("✅ Database module imported successfully")
except ImportError as e:
    print(f"❌ Database module import failed: {e}")

try:
    from utils.error_handling import HealthCheck
    print("✅ HealthCheck imported successfully")
except ImportError as e:
    print(f"❌ HealthCheck import failed: {e}")
    sys.exit(1)

# Test individual health check methods
print("\n🧪 Testing individual health check methods:")

# Test memory usage check
try:
    if psutil:
        memory_status, memory_message = HealthCheck.check_memory_usage()
        print(f"  Memory check: {memory_status} - {memory_message}")
    else:
        print("  Memory check: SKIPPED (psutil not available)")
except Exception as e:
    print(f"  Memory check: FAILED - {e}")

# Test CPU usage check
try:
    if psutil:
        cpu_status, cpu_message = HealthCheck.check_cpu_usage()
        print(f"  CPU check: {cpu_status} - {cpu_message}")
    else:
        print("  CPU check: SKIPPED (psutil not available)")
except Exception as e:
    print(f"  CPU check: FAILED - {e}")

# Test disk usage check
try:
    if psutil:
        disk_status, disk_message = HealthCheck.check_disk_usage()
        print(f"  Disk check: {disk_status} - {disk_message}")
    else:
        print("  Disk check: SKIPPED (psutil not available)")
except Exception as e:
    print(f"  Disk check: FAILED - {e}")

# Test environment variables check
try:
    env_status, env_message = HealthCheck.check_environment_variables()
    print(f"  Environment variables check: {env_status} - {env_message}")
except Exception as e:
    print(f"  Environment variables check: FAILED - {e}")

# Test SSL certificates check
try:
    ssl_status, ssl_message = HealthCheck.check_ssl_certificates()
    print(f"  SSL certificates check: {ssl_status} - {ssl_message}")
except Exception as e:
    print(f"  SSL certificates check: FAILED - {e}")

# Test cache service check
try:
    cache_status, cache_message = HealthCheck.check_cache_service()
    print(f"  Cache service check: {cache_status} - {cache_message}")
except Exception as e:
    print(f"  Cache service check: FAILED - {e}")

# Test email service check
try:
    email_status, email_message = HealthCheck.check_email_service()
    print(f"  Email service check: {email_status} - {email_message}")
except Exception as e:
    print(f"  Email service check: FAILED - {e}")

print("\n🎉 Debug script completed!")
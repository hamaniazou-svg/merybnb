#!/usr/bin/env python
"""
Test Supabase database connection
Run: python test_db_connection.py
"""
import os
from dotenv import load_dotenv
import psycopg2

# Load .env file
load_dotenv()

# Get credentials from .env
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': os.getenv('DB_PORT', '5432'),
}

print("🔍 Testing connection with credentials:")
print(f"   Host: {db_config['host']}")
print(f"   Port: {db_config['port']}")
print(f"   User: {db_config['user']}")
print(f"   Database: {db_config['database']}")
print(f"   Password: {'*' * len(db_config['password'])} ({len(db_config['password'])} chars)")
print()

try:
    print("⏳ Attempting connection...")
    conn = psycopg2.connect(**db_config)
    print("✅ SUCCESS! Connection established")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"✅ PostgreSQL Version: {db_version[0]}")
    
    cursor.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"❌ CONNECTION FAILED: {e}")
    print()
    print("🔧 Troubleshooting steps:")
    print("   1. Verify all credentials in .env match Supabase exactly")
    print("   2. If password has special chars, try URL encoding them")
    print("   3. Ensure Supabase project is ACTIVE (not paused/suspended)")
    print("   4. Check if you're using the correct region/host")
    print("   5. Try port 5432 (direct) instead of 6543 (pooler)")
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")

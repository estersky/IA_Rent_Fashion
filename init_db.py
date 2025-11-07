#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os
import sys

print("\n" + "="*60)
print("DATABASE INITIALIZATION SCRIPT")
print("="*60)

DATABASE = 'fashion_rental.db'

try:
    print(f"\nCurrent working directory: {os.getcwd()}")
    print(f"Database file will be created at: {os.path.abspath(DATABASE)}")
    
    # Connect/Create database
    print(f"\nConnecting to database...")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    print("✓ Connection successful!")
    
    # Drop existing tables if needed (optional, untuk fresh start)
    print(f"\nChecking existing tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing = cursor.fetchall()
    print(f"Existing tables: {existing}")
    
    # Create users table
    print(f"\nCreating users table...")
    cursor.execute('''
        DROP TABLE IF EXISTS users
    ''')
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Users table created!")
    
    # Create login_history table
    print(f"\nCreating login_history table...")
    cursor.execute('''
        DROP TABLE IF EXISTS login_history
    ''')
    cursor.execute('''
        CREATE TABLE login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✓ Login history table created!")
    
    # Commit changes
    conn.commit()
    print(f"\nCommitting changes...")
    print("✓ Changes committed!")
    
    # Verify tables
    print(f"\nVerifying tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables created: {tables}")
    
    # Check users table structure
    cursor.execute("PRAGMA table_info(users);")
    columns = cursor.fetchall()
    print(f"\nUsers table structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✓ DATABASE INITIALIZATION COMPLETE!")
    print("="*60)
    print(f"\nDatabase file: {os.path.abspath(DATABASE)}")
    print(f"File size: {os.path.getsize(DATABASE)} bytes")
    print("\nYou can now run: python app.py")
    print("="*60 + "\n")
    
except sqlite3.Error as e:
    print(f"\n✗ Database error: {e}")
    sys.exit(1)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
#!/usr/bin/env python3
"""
Simple test to check imports and SQLite setup
"""
try:
    print("Testing imports...")
    
    # Test basic imports
    import flask
    print("✓ Flask imported")
    
    from flask_sqlalchemy import SQLAlchemy
    print("✓ Flask-SQLAlchemy imported")
    
    from flask_login import LoginManager
    print("✓ Flask-Login imported")
    
    # Test app creation
    from app import create_app
    print("✓ App factory imported")
    
    app = create_app()
    print("✓ App created successfully")
    
    print("All imports working! Database should be ready for SQLite.")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please install missing packages with: pip install -r requirements.txt")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

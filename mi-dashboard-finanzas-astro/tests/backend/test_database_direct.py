#!/usr/bin/env python3
"""
Script to test database connection and schema directly.
"""

import sqlite3
from utils.bd import DatabaseManager

print("=== Testing direct SQLite connection ===")
conn = sqlite3.connect('data/finanzas.db')
cursor = conn.cursor()

# Test direct query
try:
    cursor.execute('SELECT id, detalle, categoria, tipo_regla FROM transacciones LIMIT 2')
    results = cursor.fetchall()
    print(f"Direct SQLite query successful: {len(results)} rows")
    for row in results:
        print(f"  ID: {row[0]}, Detail: {row[1][:30]}..., Category: {row[2]}, Rule: {row[3]}")
except Exception as e:
    print(f"Direct SQLite query failed: {e}")

conn.close()

print("\n=== Testing DatabaseManager ===")
try:
    db_manager = DatabaseManager()
    print("DatabaseManager created successfully")
    
    # Try to query through SQLAlchemy
    from utils.bd import Transaccion
    transactions = db_manager.session.query(Transaccion).limit(2).all()
    print(f"SQLAlchemy query successful: {len(transactions)} rows")
    for t in transactions:
        print(f"  ID: {t.id}, Detail: {t.detalle[:30]}..., Category: {t.categoria}")
        
except Exception as e:
    print(f"DatabaseManager failed: {e}")

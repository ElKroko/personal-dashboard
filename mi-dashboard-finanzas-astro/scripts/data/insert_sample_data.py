#!/usr/bin/env python3
"""
Script to add sample uncategorized transactions for testing categorization functionality.
"""

import sqlite3
from datetime import datetime, date

# Sample uncategorized transactions for testing
sample_transactions = [
    {
        'fecha': '2025-03-01',
        'detalle': 'TRANSFERENCIA A JUAN PEREZ',
        'monto': -50000.0,
        'tipo': 'GASTO',
        'categoria': 'Sin categorizar',
        'año': 2025,
        'mes': 3,
        'dia': 1,
        'semana': 9,
        'tipo_regla': 'sin_coincidencias'
    },
    {
        'fecha': '2025-03-02',
        'detalle': 'COMPRA SUPERMERCADO LIDER',
        'monto': -25000.0,
        'tipo': 'GASTO',
        'categoria': 'Sin categorizar',
        'año': 2025,
        'mes': 3,
        'dia': 2,
        'semana': 9,
        'tipo_regla': 'sin_coincidencias'
    },
    {
        'fecha': '2025-03-03',
        'detalle': 'PAGO APPLE STORE',
        'monto': -15000.0,
        'tipo': 'GASTO',
        'categoria': 'Sin categorizar',
        'año': 2025,
        'mes': 3,
        'dia': 3,
        'semana': 9,
        'tipo_regla': 'sin_coincidencias'
    },
    {
        'fecha': '2025-03-04',
        'detalle': 'COMPRA TABAQUERIA',
        'monto': -5000.0,
        'tipo': 'GASTO',
        'categoria': 'Sin categorizar',
        'año': 2025,
        'mes': 3,
        'dia': 4,
        'semana': 9,
        'tipo_regla': 'sin_coincidencias'
    },
    {
        'fecha': '2025-03-05',
        'detalle': 'PAGO UBER TRIP',
        'monto': -8000.0,
        'tipo': 'GASTO',
        'categoria': 'Sin categorizar',
        'año': 2025,
        'mes': 3,
        'dia': 5,
        'semana': 9,
        'tipo_regla': 'sin_coincidencias'
    }
]

# Connect to database and insert sample data
conn = sqlite3.connect('data/finanzas.db')
cursor = conn.cursor()

for transaction in sample_transactions:
    cursor.execute('''
        INSERT INTO transacciones (
            fecha, detalle, monto, tipo, categoria, año, mes, dia, semana, 
            tipo_regla, created_at, fecha_modificacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        transaction['fecha'],
        transaction['detalle'],
        transaction['monto'],
        transaction['tipo'],
        transaction['categoria'],
        transaction['año'],
        transaction['mes'],
        transaction['dia'],
        transaction['semana'],
        transaction['tipo_regla'],
        datetime.now(),
        datetime.now()
    ))

conn.commit()

# Verify data was inserted
cursor.execute('SELECT COUNT(*) FROM transacciones')
count = cursor.fetchone()[0]
print(f'Successfully inserted {count} sample transactions')

cursor.execute('SELECT id, detalle, categoria FROM transacciones LIMIT 3')
results = cursor.fetchall()
print('Sample transactions:')
for row in results:
    print(f'  ID: {row[0]}, Detail: {row[1]}, Category: {row[2]}')

conn.close()

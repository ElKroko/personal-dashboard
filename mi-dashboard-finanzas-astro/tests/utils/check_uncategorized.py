#!/usr/bin/env python3
"""
Script para verificar transacciones sin categorizar.
"""

import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('data/finanzas.db')
cursor = conn.cursor()

# Buscar transacciones sin categorizar
cursor.execute('''
    SELECT id, detalle, monto, categoria 
    FROM transacciones 
    WHERE categoria = "Sin categorizar" OR categoria IS NULL OR categoria = ""
''')

results = cursor.fetchall()

print("Transacciones sin categorizar:")
print(f"Total encontradas: {len(results)}")
print("-" * 50)

for row in results:
    print(f"ID: {row[0]}")
    print(f"Detalle: {row[1]}")
    print(f"Monto: {row[2]}")
    print(f"Categoría: '{row[3]}'")
    print("-" * 30)

conn.close()

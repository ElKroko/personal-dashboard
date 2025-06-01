#!/usr/bin/env python3
"""
Script para añadir categorías por defecto a la base de datos.
"""

import sqlite3
from datetime import datetime

# Categorías comunes para transacciones
categorias_defaults = [
    "Gasto - Alimentos",
    "Gasto - Transporte", 
    "Gasto - Entretenimiento",
    "Gasto - Servicios Básicos",
    "Gasto - Salud",
    "Gasto - Educación",
    "Gasto - Vestimenta",
    "Gasto - Hogar",
    "Gasto - Tecnología",
    "Gasto - Otros",
    "Transferencias",
    "Ingreso - Sueldo",
    "Ingreso - Otros",
    "Ahorro",
    "Inversión"
]

# Conectar a la base de datos
conn = sqlite3.connect('data/finanzas.db')
cursor = conn.cursor()

# Insertar algunas transacciones con categorías para que aparezcan como disponibles
print("Añadiendo transacciones con categorías por defecto...")

# Insertamos una transacción pequeña para cada categoría
for i, categoria in enumerate(categorias_defaults):
    cursor.execute('''
        INSERT OR IGNORE INTO transacciones 
        (fecha, detalle, monto, tipo, categoria, año, mes, dia, semana, tipo_regla, created_at, fecha_modificacion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        '2025-01-01',
        f'Transacción de referencia para {categoria}',
        1.0,  # Monto pequeño
        'Gasto' if categoria.startswith('Gasto') else 'Ingreso' if categoria.startswith('Ingreso') else 'Otro',
        categoria,
        2025,
        1,
        1,
        1,
        'manual',
        datetime.now(),
        datetime.now()
    ))

print(f"Se añadieron {len(categorias_defaults)} categorías de referencia")
conn.commit()

# Verificar que se insertaron correctamente
cursor.execute('SELECT DISTINCT categoria FROM transacciones ORDER BY categoria')
categorias_db = cursor.fetchall()

print("\nCategorías disponibles en la base de datos:")
for cat in categorias_db:
    print(f"- {cat[0]}")

conn.close()
print("\n¡Categorías añadidas exitosamente!")

#!/usr/bin/env python3
"""
Script to recreate the transactions table with the correct schema.
"""

import sqlite3
import shutil
from datetime import datetime

# Backup
backup_name = f'data/finanzas_backup_recreate_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
shutil.copy('data/finanzas.db', backup_name)
print(f'Backup created: {backup_name}')

# Connect and recreate table
conn = sqlite3.connect('data/finanzas.db')
cursor = conn.cursor()

# Drop and recreate table
cursor.execute('DROP TABLE IF EXISTS transacciones')
cursor.execute('''
CREATE TABLE transacciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE NOT NULL,
    detalle VARCHAR(500) NOT NULL,
    monto FLOAT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    año INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    semana INTEGER NOT NULL,
    tipo_regla TEXT DEFAULT "mapeo_por_palabra_clave",
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

print('Table recreated successfully')
conn.commit()
conn.close()
print('Database schema updated!')

#!/usr/bin/env python3
"""
Script de migración de base de datos para agregar las nuevas columnas.
"""

import os
import sqlite3
import shutil
from datetime import datetime
import sys

def migrate_database():
    """
    Migra la base de datos agregando las columnas faltantes.
    """
    db_path = 'data/finanzas.db'
    backup_path = f'data/finanzas_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    if not os.path.exists(db_path):
        print("No se encontró la base de datos. Se creará una nueva.")
        return create_new_database()
    
    try:
        # Hacer backup
        shutil.copy(db_path, backup_path)
        print(f"Backup creado: {backup_path}")
        
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(transacciones)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"Columnas actuales: {columns}")
        
        # Agregar las columnas faltantes si no existen
        new_columns = [
            ('tipo_regla', 'TEXT DEFAULT "mapeo_por_palabra_clave"'),
            ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('fecha_modificacion', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]
        
        for column_name, column_def in new_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE transacciones ADD COLUMN {column_name} {column_def}')
                    print(f"Columna '{column_name}' agregada correctamente")
                except sqlite3.Error as e:
                    print(f"Error al agregar columna '{column_name}': {e}")
        
        conn.commit()
        conn.close()
        
        print("Migración completada exitosamente")
        return True
        
    except Exception as e:
        print(f"Error durante la migración: {e}")
        # Restaurar backup si algo salió mal
        if os.path.exists(backup_path):
            shutil.copy(backup_path, db_path)
            print("Base de datos restaurada desde backup")
        return False

def create_new_database():
    """
    Crea una nueva base de datos con el esquema correcto.
    """
    try:
        from utils.bd import DatabaseManager
        db = DatabaseManager()
        print("Nueva base de datos creada con esquema correcto")
        return True
    except Exception as e:
        print(f"Error al crear nueva base de datos: {e}")
        return False

def test_database():
    """
    Prueba que la base de datos funcione correctamente.
    """
    try:
        from utils.bd import DatabaseManager
        db = DatabaseManager()
        count = db.contar_transacciones()
        print(f"Test exitoso: {count} transacciones en la base de datos")
        return True
    except Exception as e:
        print(f"Error en el test: {e}")
        return False

if __name__ == "__main__":
    print("=== Migración de Base de Datos ===")
    
    if migrate_database():
        print("\n=== Probando base de datos ===")
        if test_database():
            print("\n✅ Migración completada exitosamente")
        else:
            print("\n❌ Error en las pruebas post-migración")
            sys.exit(1)
    else:
        print("\n❌ Error en la migración")
        sys.exit(1)

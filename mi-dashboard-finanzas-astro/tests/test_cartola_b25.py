#!/usr/bin/env python3
"""
Test para verificar el formato de cartola comenzando en B25
"""

import pandas as pd
import os

def test_cartola_b25():
    """Test para verificar lectura desde B25"""
    archivo = "F:/Codes/FINANZAS PERSONALES/personal-dashboard/mi-dashboard-finanzas-astro/backend/data/load_excels/cartola_28022025.xls"
    
    print("🔍 Analizando formato cartola desde B25...")
    
    try:
        # Leer desde fila 24 (índice 23) ya que Excel es base 1
        df = pd.read_excel(archivo, header=23)
        
        print(f"📊 Dimensiones: {df.shape}")
        print(f"📋 Columnas: {list(df.columns)}")
        
        if len(df) > 0:
            print(f"\n📋 Primeras 5 filas:")
            print(df.head(5))
            
            print(f"\n🔍 Tipos de datos:")
            for col in df.columns:
                print(f"  - {col}: {df[col].dtype}")
                
        return df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_cartola_b25()

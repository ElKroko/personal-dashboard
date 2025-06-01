#!/usr/bin/env python3
"""
Test específico para diagnosticar y arreglar el warning de fechas
"""

import sys
import os
import warnings
import pandas as pd

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_date_parsing():
    """Test diferentes métodos de parsing de fechas"""
    print("🔍 DIAGNÓSTICO DE PARSING DE FECHAS")
    print("=" * 50)
    
    # Capturar warnings
    warnings.simplefilter("always")
    
    # Datos de ejemplo con diferentes formatos de fecha
    test_dates = [
        '2024-01-15',  # YYYY-MM-DD
        '15/01/2024',  # DD/MM/YYYY
        '01/15/2024',  # MM/DD/YYYY
        '2024-12-31',  # YYYY-MM-DD
        '31/12/2024'   # DD/MM/YYYY
    ]
    
    print("Fechas de prueba:", test_dates)
    
    # Test 1: Método actual (que genera warning)
    print("\n1. Método actual (con dayfirst=True):")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            df_test = pd.DataFrame({'fecha': test_dates})
            df_test['fecha_parsed'] = pd.to_datetime(df_test['fecha'], dayfirst=True, errors='coerce')
            
            print(f"   Resultados: {df_test['fecha_parsed'].tolist()}")
            if w:
                print(f"   ⚠️ Warnings generados: {len(w)}")
                for warning in w:
                    print(f"      - {warning.message}")
            else:
                print("   ✅ Sin warnings")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Método mejorado (sin warnings)
    print("\n2. Método mejorado (detectar formato automáticamente):")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            df_test = pd.DataFrame({'fecha': test_dates})
            
            # Intentar múltiples formatos
            df_test['fecha_parsed'] = pd.to_datetime(df_test['fecha'], errors='coerce')
            
            print(f"   Resultados: {df_test['fecha_parsed'].tolist()}")
            if w:
                print(f"   ⚠️ Warnings generados: {len(w)}")
                for warning in w:
                    print(f"      - {warning.message}")
            else:
                print("   ✅ Sin warnings")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Método con formatos específicos
    print("\n3. Método con formatos específicos:")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            df_test = pd.DataFrame({'fecha': test_dates})
            
            def parse_fecha_inteligente(fecha_str):
                """Parse fecha probando múltiples formatos"""
                formatos = [
                    '%Y-%m-%d',  # 2024-01-15
                    '%d/%m/%Y',  # 15/01/2024
                    '%m/%d/%Y',  # 01/15/2024
                    '%Y/%m/%d',  # 2024/01/15
                    '%d-%m-%Y',  # 15-01-2024
                ]
                
                for formato in formatos:
                    try:
                        return pd.to_datetime(fecha_str, format=formato)
                    except (ValueError, TypeError):
                        continue
                
                # Si nada funciona, usar el parser automático
                return pd.to_datetime(fecha_str, errors='coerce')
            
            df_test['fecha_parsed'] = df_test['fecha'].apply(parse_fecha_inteligente)
            
            print(f"   Resultados: {df_test['fecha_parsed'].tolist()}")
            if w:
                print(f"   ⚠️ Warnings generados: {len(w)}")
                for warning in w:
                    print(f"      - {warning.message}")
            else:
                print("   ✅ Sin warnings")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_real_tef_file():
    """Test con archivos TEF reales"""
    print("\n🔍 TEST CON ARCHIVOS TEF REALES")
    print("=" * 50)
    
    try:
        load_excels_path = os.path.join('backend', 'data', 'load_excels')
        
        if not os.path.exists(load_excels_path):
            print(f"❌ Directorio no existe: {load_excels_path}")
            return
            
        archivos = [f for f in os.listdir(load_excels_path) if f.endswith('.xlsx')]
        
        if not archivos:
            print("❌ No se encontraron archivos TEF")
            return
            
        archivo_test = os.path.join(load_excels_path, archivos[0])
        print(f"Probando con: {archivo_test}")
        
        # Leer archivo crudo
        df_raw = pd.read_excel(archivo_test, header=11)
        print(f"Filas leídas: {len(df_raw)}")
        
        if 'Fecha' in df_raw.columns:
            fechas_sample = df_raw['Fecha'].dropna().head(5)
            print(f"Muestra de fechas originales: {fechas_sample.tolist()}")
            print(f"Tipos de fechas: {fechas_sample.dtypes}")
            
            # Test parsing con warnings capturados
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                # Método actual
                fechas_parsed = pd.to_datetime(fechas_sample, dayfirst=True, errors='coerce')
                print(f"Fechas parseadas: {fechas_parsed.tolist()}")
                
                if w:
                    print(f"⚠️ Warnings capturados: {len(w)}")
                    for warning in w:
                        print(f"   - {warning.message}")
                else:
                    print("✅ Sin warnings")
        else:
            print("❌ No se encontró columna 'Fecha' en el archivo")
            print(f"Columnas disponibles: {df_raw.columns.tolist()}")
            
    except Exception as e:
        print(f"❌ Error procesando archivo TEF: {e}")
        import traceback
        traceback.print_exc()

def generate_fixed_code():
    """Genera el código corregido para leer_excel.py"""
    print("\n💡 CÓDIGO CORREGIDO PARA leer_excel.py")
    print("=" * 50)
    
    fixed_code = '''
def parse_fecha_robusta(fecha_serie):
    """
    Parse fechas de manera robusta sin generar warnings
    """
    # Si ya es datetime, devolver tal como está
    if pd.api.types.is_datetime64_any_dtype(fecha_serie):
        return fecha_serie
    
    # Convertir a string si no lo es
    fecha_serie = fecha_serie.astype(str)
    
    # Intentar parsing automático primero (sin dayfirst para evitar warnings)
    try:
        return pd.to_datetime(fecha_serie, errors='coerce')
    except:
        pass
    
    # Si eso falla, intentar formatos específicos
    formatos = [
        '%Y-%m-%d',   # 2024-01-15
        '%d/%m/%Y',   # 15/01/2024  
        '%m/%d/%Y',   # 01/15/2024
        '%Y/%m/%d',   # 2024/01/15
        '%d-%m-%Y',   # 15-01-2024
        '%Y%m%d',     # 20240115
    ]
    
    for formato in formatos:
        try:
            return pd.to_datetime(fecha_serie, format=formato, errors='coerce')
        except:
            continue
    
    # Último recurso: usar dayfirst=False para evitar warnings
    return pd.to_datetime(fecha_serie, dayfirst=False, errors='coerce')

# Reemplazar línea 39 en leer_excel.py:
# df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
# 
# Por:
# df['fecha'] = parse_fecha_robusta(df['fecha'])
'''
    
    print(fixed_code)

if __name__ == "__main__":
    test_date_parsing()
    test_real_tef_file()
    generate_fixed_code()

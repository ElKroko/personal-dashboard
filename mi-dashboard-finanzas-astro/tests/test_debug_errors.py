#!/usr/bin/env python3
"""
Test para diagnosticar los errores 500 en los endpoints
Ejecutar en una consola separada mientras el servidor está corriendo
"""

import sys
import os
import requests
import json
import traceback

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_endpoint(url, method='GET', data=None):
    """Test un endpoint específico y muestra información detallada"""
    print(f"\n{'='*50}")
    print(f"Testing {method} {url}")
    print(f"{'='*50}")
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response JSON:")
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(f"Response Text: {response.text}")
            
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que el backend esté corriendo en http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        traceback.print_exc()
        return False

def test_file_processing():
    """Test directo del procesamiento de archivos sin usar el servidor"""
    print(f"\n{'='*50}")
    print("Testing file processing directly")
    print(f"{'='*50}")
    
    try:
        from utils.leer_excel import procesar_archivo_excel
        from utils.categorizar import aplicar_categorizacion
        from utils.fechas import agregar_columnas_tiempo
        from utils.agregaciones import calcular_todas_agregaciones
        
        # Buscar archivos TEF
        load_excels_path = os.path.join('backend', 'data', 'load_excels')
        print(f"Buscando archivos en: {os.path.abspath(load_excels_path)}")
        
        if not os.path.exists(load_excels_path):
            print(f"❌ Directorio no existe: {load_excels_path}")
            return False
            
        archivos = [f for f in os.listdir(load_excels_path) if f.endswith(('.xlsx', '.xls'))]
        print(f"Archivos encontrados: {archivos}")
        
        if not archivos:
            print("❌ No se encontraron archivos Excel")
            return False
            
        # Probar con el primer archivo
        archivo_test = os.path.join(load_excels_path, archivos[0])
        print(f"\nProcesando: {archivo_test}")
        
        # 1. Procesar archivo
        print("1. Procesando archivo Excel...")
        df = procesar_archivo_excel(archivo_test)
        print(f"   ✅ Filas procesadas: {len(df)}")
        print(f"   ✅ Columnas: {list(df.columns)}")
        
        # 2. Aplicar categorización
        print("2. Aplicando categorización...")
        df = aplicar_categorizacion(df)
        print(f"   ✅ Categorías: {df['categoria'].unique()}")
        
        # 3. Agregar columnas de tiempo
        print("3. Agregando columnas de tiempo...")
        df = agregar_columnas_tiempo(df)
        print(f"   ✅ Nuevas columnas de fecha agregadas")
        
        # 4. Calcular agregaciones
        print("4. Calculando agregaciones...")
        agregaciones = calcular_todas_agregaciones(df)
        print(f"   ✅ Agregaciones calculadas: {list(agregaciones.keys())}")
        
        print("\n✅ Procesamiento directo de archivos EXITOSO")
        return True
        
    except Exception as e:
        print(f"❌ Error en procesamiento directo: {e}")
        traceback.print_exc()
        return False

def test_database_connection():
    """Test la conexión a la base de datos"""
    print(f"\n{'='*50}")
    print("Testing database connection")
    print(f"{'='*50}")
    
    try:
        from utils.bd import DatabaseManager
        
        db_manager = DatabaseManager()
        print("✅ DatabaseManager creado exitosamente")
        
        # Test básico de la BD
        count = db_manager.contar_transacciones()
        print(f"✅ Transacciones en BD: {count}")
        
        db_manager.cerrar_conexion()
        print("✅ Conexión cerrada exitosamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        traceback.print_exc()
        return False

def main():
    """Ejecutar todos los tests de diagnóstico"""
    print("🔍 DIAGNÓSTICO DE ERRORES DEL DASHBOARD FINANCIERO")
    print("=" * 60)
    
    # Test 1: Verificar conexión al servidor
    server_ok = test_endpoint("http://localhost:8000/")
    
    if not server_ok:
        print("\n⚠️ El servidor no está respondiendo. Iniciando tests offline...")
    
    # Test 2: Verificar endpoint de stats
    if server_ok:
        test_endpoint("http://localhost:8000/stats/")
    
    # Test 3: Test directo de procesamiento de archivos
    processing_ok = test_file_processing()
    
    # Test 4: Test de base de datos
    db_ok = test_database_connection()
    
    # Test 5: Test de endpoints problemáticos (solo si el servidor está ok)
    if server_ok:
        print("\n🔍 Testing endpoints problemáticos...")
        test_endpoint("http://localhost:8000/cargar-tef-locales/", method='POST')
        test_endpoint("http://localhost:8000/historial/")
    
    # Resumen
    print(f"\n{'='*60}")
    print("📊 RESUMEN DE DIAGNÓSTICO")
    print(f"{'='*60}")
    print(f"🌐 Servidor respondiendo: {'✅' if server_ok else '❌'}")
    print(f"📁 Procesamiento de archivos: {'✅' if processing_ok else '❌'}")
    print(f"🗄️ Base de datos: {'✅' if db_ok else '❌'}")
    
    if not processing_ok:
        print("\n💡 RECOMENDACIONES:")
        print("   - Verificar que los archivos Excel existan en backend/data/load_excels/")
        print("   - Verificar que las dependencias estén instaladas: pip install -r requirements.txt")
        print("   - Revisar el formato de los archivos Excel")
        
    if server_ok and not db_ok:
        print("\n💡 Problema con base de datos detectado - verificar SQLAlchemy")

if __name__ == "__main__":
    main()

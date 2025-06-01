#!/usr/bin/env python3
"""
Test específico para los endpoints que están dando error 500
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def check_server():
    """Verificar que el servidor esté corriendo"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_stats_endpoint():
    """Test del endpoint /stats/"""
    print("\n🔍 Testing /stats/ endpoint")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/stats/", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cargar_tef_endpoint():
    """Test del endpoint /cargar-tef-locales/"""
    print("\n🔍 Testing /cargar-tef-locales/ endpoint")
    print("-" * 40)
    
    try:
        response = requests.post(f"{BASE_URL}/cargar-tef-locales/", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Processed {data.get('total_transacciones', 0)} transactions")
            print(f"Files: {data.get('archivos_procesados', [])}")
            print(f"BD Status: {data.get('bd_status', 'Unknown')}")
            return True
        else:
            try:
                error_data = response.json()
                print(f"❌ Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"❌ Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_historial_endpoint():
    """Test del endpoint /historial/"""
    print("\n🔍 Testing /historial/ endpoint")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/historial/", timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data.get('total_transacciones', 0)} transactions")
            print(f"Message: {data.get('message', 'No message')}")
            return True
        else:
            try:
                error_data = response.json()
                print(f"❌ Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"❌ Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_procesar_endpoint():
    """Test del endpoint /procesar/ (sin archivo, solo para ver error)"""
    print("\n🔍 Testing /procesar/ endpoint (sin archivo)")
    print("-" * 40)
    
    try:
        # Test sin archivo para ver si el endpoint responde
        response = requests.post(f"{BASE_URL}/procesar/", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 422:  # Expected - validation error
            print("✅ Endpoint responde correctamente (error de validación esperado)")
            return True
        else:
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def wait_for_server(max_attempts=5):
    """Esperar a que el servidor esté disponible"""
    print("🔄 Esperando que el servidor esté disponible...")
    
    for attempt in range(max_attempts):
        if check_server():
            print("✅ Servidor disponible!")
            return True
        
        print(f"   Intento {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    
    print("❌ Servidor no disponible después de esperar")
    return False

def main():
    print("🧪 TEST DE ENDPOINTS DEL DASHBOARD FINANCIERO")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    if not check_server():
        if not wait_for_server():
            print("\n❌ No se pudo conectar al servidor.")
            print("   Asegúrate de que el backend esté corriendo:")
            print("   cd backend && python app.py")
            return
    
    # Ejecutar tests
    results = {
        'stats': test_stats_endpoint(),
        'cargar_tef': test_cargar_tef_endpoint(),
        'historial': test_historial_endpoint(),
        'procesar': test_procesar_endpoint()
    }
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    
    for endpoint, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{endpoint:15} : {status}")
    
    total_passed = sum(results.values())
    print(f"\nTotal: {total_passed}/{len(results)} tests pasaron")
    
    if total_passed == len(results):
        print("🎉 Todos los endpoints están funcionando!")
    else:
        print("⚠️ Algunos endpoints tienen problemas.")
        print("\nSugerencias:")
        if not results['cargar_tef']:
            print("- Verificar que existan archivos Excel en backend/data/load_excels/")
            print("- Verificar permisos de lectura de archivos")
        if not results['historial']:
            print("- Verificar conexión a la base de datos")
            print("- Verificar que SQLAlchemy esté instalado")

if __name__ == "__main__":
    main()

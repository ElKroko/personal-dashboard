#!/usr/bin/env python3
"""
Test específico para verificar el fix del endpoint /cargar-tef-locales/
y el manejo de serialización JSON
"""

import os
import sys
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime

def print_separador(titulo):
    """Imprime un separador visual para organizar la salida"""
    print("\n" + "="*60)
    print(f"  {titulo}")
    print("="*60)

def test_limpiar_datos_json():
    """Test de la función limpiar_datos_para_json"""
    print_separador("TEST FUNCIÓN LIMPIEZA JSON")
    
    # Agregar el directorio backend al path
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    sys.path.insert(0, backend_path)
    
    # Importar la función desde app.py
    try:
        from app import limpiar_datos_para_json
        print("✅ Función importada correctamente")
    except ImportError as e:
        print(f"❌ Error importando función: {e}")
        return False
    
    # Crear datos de prueba problemáticos
    datos_problema = {
        "valores_nan": [np.nan, float('nan'), pd.NaT],
        "valores_inf": [np.inf, -np.inf, float('inf')],
        "timestamps": [pd.Timestamp('2025-05-31'), pd.Timestamp('2025-04-01')],
        "numeros_normales": [1, 2.5, np.int64(10), np.float64(15.5)],
        "texto": "Texto normal",
        "lista_mixta": [1, np.nan, pd.Timestamp('2025-05-31'), "texto"],
        "dict_anidado": {
            "timestamp": pd.Timestamp('2025-05-31'),
            "nan_value": np.nan,
            "inf_value": np.inf,
            "normal": 42
        }
    }
    
    print("🧪 Probando función de limpieza...")
    try:
        datos_limpios = limpiar_datos_para_json(datos_problema)
        print("✅ Función de limpieza ejecutada sin errores")
        
        # Verificar que los valores problemáticos se han convertido
        print("\n📋 Resultados de limpieza:")
        print(f"  - valores_nan: {datos_limpios['valores_nan']}")
        print(f"  - valores_inf: {datos_limpios['valores_inf']}")
        print(f"  - timestamps: {datos_limpios['timestamps']}")
        print(f"  - lista_mixta: {datos_limpios['lista_mixta']}")
        print(f"  - dict_anidado: {datos_limpios['dict_anidado']}")
        
        # Probar serialización JSON
        try:
            json_string = json.dumps(datos_limpios)
            print("✅ Serialización JSON exitosa")
            print(f"📏 Tamaño JSON: {len(json_string)} caracteres")
            return True
        except Exception as e:
            print(f"❌ Error en serialización JSON: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error en función de limpieza: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_endpoint_cargar_tef():
    """Test del endpoint /cargar-tef-locales/"""
    print_separador("TEST ENDPOINT /cargar-tef-locales/")
    
    url = "http://localhost:8000/cargar-tef-locales/"
    
    print("🌐 Probando endpoint...")
    try:
        response = requests.post(url, timeout=30)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Endpoint responde correctamente")
            
            # Intentar parsear JSON
            try:
                data = response.json()
                print("✅ JSON parseado correctamente")
                
                # Verificar estructura de respuesta
                print(f"\n📊 Estructura de respuesta:")
                for clave, valor in data.items():
                    if isinstance(valor, list):
                        print(f"  - {clave}: lista con {len(valor)} elementos")
                    elif isinstance(valor, dict):
                        print(f"  - {clave}: diccionario con {len(valor)} claves")
                    else:
                        print(f"  - {clave}: {type(valor).__name__}")
                
                # Verificar campos específicos
                if 'status' in data:
                    print(f"📈 Status: {data['status']}")
                if 'total_transacciones' in data:
                    print(f"📊 Total transacciones: {data['total_transacciones']}")
                if 'archivos_procesados' in data:
                    print(f"📁 Archivos procesados: {data['archivos_procesados']}")
                
                # Verificar que no hay valores problemáticos en la respuesta
                def verificar_valores_problematicos(obj, ruta=""):
                    problemas = []
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            problemas.extend(verificar_valores_problematicos(v, f"{ruta}.{k}"))
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            problemas.extend(verificar_valores_problematicos(item, f"{ruta}[{i}]"))
                    elif obj is None:
                        pass  # None es válido
                    elif isinstance(obj, float):
                        if np.isnan(obj) or np.isinf(obj):
                            problemas.append(f"Valor problemático en {ruta}: {obj}")
                    return problemas
                
                problemas = verificar_valores_problematicos(data)
                if problemas:
                    print(f"⚠️  Valores problemáticos encontrados:")
                    for problema in problemas[:5]:  # Mostrar solo los primeros 5
                        print(f"    {problema}")
                else:
                    print("✅ No se encontraron valores problemáticos en JSON")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Error parseando JSON: {e}")
                print(f"📄 Respuesta raw: {response.text[:500]}...")
                return False
                
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error: {error_data}")
            except:
                print(f"📄 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose en localhost:8000?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout al conectar con el servidor")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_endpoint_historial():
    """Test del endpoint /historial/"""
    print_separador("TEST ENDPOINT /historial/")
    
    url = "http://localhost:8000/historial/"
    
    print("🌐 Probando endpoint historial...")
    try:
        response = requests.get(url, timeout=30)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Endpoint historial responde correctamente")
            
            try:
                data = response.json()
                print("✅ JSON parseado correctamente")
                
                if 'total_transacciones' in data:
                    print(f"📊 Total transacciones en historial: {data['total_transacciones']}")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Error parseando JSON historial: {e}")
                return False
        else:
            print(f"❌ Error en endpoint historial: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor para historial")
        return False
    except Exception as e:
        print(f"❌ Error en historial: {e}")
        return False

def verificar_servidor():
    """Verifica que el servidor esté ejecutándose"""
    print_separador("VERIFICACIÓN DEL SERVIDOR")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está ejecutándose")
            return True
        else:
            print(f"⚠️  Servidor responde pero con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Servidor no está ejecutándose en localhost:8000")
        print("💡 Para iniciar el servidor, ejecuta: python backend/app.py")
        return False
    except Exception as e:
        print(f"❌ Error verificando servidor: {e}")
        return False

def main():
    """Función principal del test"""
    print_separador("TEST DE ENDPOINTS Y SERIALIZACIÓN JSON")
    print(f"🕐 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Test de función de limpieza
    limpieza_ok = test_limpiar_datos_json()
    
    # 2. Verificar servidor
    servidor_ok = verificar_servidor()
    
    if not servidor_ok:
        print("\n❌ No se pueden ejecutar tests de endpoints sin servidor")
        return
    
    # 3. Test endpoint cargar TEF
    cargar_ok = test_endpoint_cargar_tef()
    
    # 4. Test endpoint historial
    historial_ok = test_endpoint_historial()
    
    # Resumen final
    print_separador("RESUMEN FINAL")
    print(f"🧹 Función limpieza JSON: {'✅' if limpieza_ok else '❌'}")
    print(f"🌐 Servidor disponible: {'✅' if servidor_ok else '❌'}")
    print(f"📤 Endpoint cargar TEF: {'✅' if cargar_ok else '❌'}")
    print(f"📊 Endpoint historial: {'✅' if historial_ok else '❌'}")
    
    if limpieza_ok and cargar_ok and historial_ok:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("Los endpoints deberían funcionar correctamente ahora")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisar logs arriba.")
    
    print(f"\n🕐 Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

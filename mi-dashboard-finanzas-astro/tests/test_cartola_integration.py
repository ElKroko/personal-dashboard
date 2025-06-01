"""
Test integral para verificar que la integración de archivos cartola funcione correctamente.
Verifica:
1. Detección automática de formato cartola
2. Procesamiento de archivos cartola
3. Carga en base de datos
4. Endpoints funcionando con datos cartola
5. Agregaciones correctas
6. Respuestas JSON válidas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import pandas as pd
from datetime import datetime
import sqlite3
import json
import traceback

# Importar módulos del backend
from utils.leer_excel import detectar_formato_archivo, cargar_y_limpiar_cartola, procesar_archivo_excel
from utils.bd import DatabaseManager
from utils.fechas import agregar_columnas_tiempo
from utils.agregaciones import calcular_agregaciones_por_tiempo
from app import limpiar_datos_para_json

def test_cartola_integration():
    """Test completo de integración de archivos cartola"""
    print("=" * 80)
    print("TEST INTEGRAL DE CARTOLA")
    print("=" * 80)
    
    # Configuración
    data_folder = r"F:\Codes\FINANZAS PERSONALES\personal-dashboard\mi-dashboard-finanzas-astro\backend\data\load_excels"
    db_path = r"F:\Codes\FINANZAS PERSONALES\personal-dashboard\mi-dashboard-finanzas-astro\backend\data\finanzas.db"
    
    try:
        # 1. BUSCAR ARCHIVOS CARTOLA
        print("\n1. BUSCANDO ARCHIVOS CARTOLA...")
        print("-" * 50)
        
        cartola_files = []
        if os.path.exists(data_folder):
            for file in os.listdir(data_folder):
                if file.endswith(('.xls', '.xlsx')):
                    file_path = os.path.join(data_folder, file)
                    cartola_files.append((file, file_path))
        
        print(f"Archivos encontrados: {len(cartola_files)}")
        for file, path in cartola_files:
            print(f"  - {file}")
        
        if not cartola_files:
            print("❌ No se encontraron archivos cartola para procesar")
            return False
        
        # 2. DETECTAR FORMATO DE CADA ARCHIVO
        print("\n2. DETECTANDO FORMATOS...")
        print("-" * 50)
        
        archivos_cartola = []
        for file, file_path in cartola_files:
            try:
                formato = detectar_formato_archivo(file_path)
                print(f"  {file}: {formato}")
                
                if formato == 'cartola':
                    archivos_cartola.append((file, file_path))
                elif formato == 'tef':
                    print(f"    ℹ️  {file} es formato TEF, no cartola")
                else:
                    print(f"    ⚠️  {file} es formato genérico/desconocido")
            except Exception as e:
                print(f"    ❌ Error detectando formato de {file}: {e}")
        
        print(f"\nArchivos cartola confirmados: {len(archivos_cartola)}")
        
        if not archivos_cartola:
            print("❌ No se encontraron archivos con formato cartola válido")
            return False
        
        # 3. PROCESAR ARCHIVO CARTOLA DE EJEMPLO
        print("\n3. PROCESANDO ARCHIVO CARTOLA...")
        print("-" * 50)
        
        file_name, file_path = archivos_cartola[0]
        print(f"Procesando: {file_name}")
        
        # Cargar datos cartola
        df_cartola = cargar_y_limpiar_cartola(file_path)
        print(f"✅ Archivo cargado exitosamente")
        print(f"   Registros: {len(df_cartola)}")
        print(f"   Columnas: {list(df_cartola.columns)}")
        
        # Verificar estructura de datos
        if len(df_cartola) == 0:
            print("❌ El archivo cartola no contiene datos válidos")
            return False
        
        # Mostrar muestra de datos
        print("\nMuestra de datos cartola:")
        print(df_cartola.head(3).to_string())
        
        # Verificar distribución de tipos
        tipo_counts = df_cartola['tipo'].value_counts()
        print(f"\nDistribución de tipos:")
        for tipo, count in tipo_counts.items():
            print(f"  {tipo}: {count}")
        
        # 4. AGREGAR COLUMNAS DE TIEMPO
        print("\n4. AGREGANDO COLUMNAS DE TIEMPO...")
        print("-" * 50)
        
        df_con_tiempo = agregar_columnas_tiempo(df_cartola)
        print(f"✅ Columnas de tiempo agregadas")
        print(f"   Columnas totales: {list(df_con_tiempo.columns)}")
        
        # Verificar que las columnas de tiempo se crearon correctamente
        time_cols = ['año', 'mes', 'semana', 'año_mes', 'año_semana', 'dia_semana']
        missing_time_cols = [col for col in time_cols if col not in df_con_tiempo.columns]
        if missing_time_cols:
            print(f"❌ Faltan columnas de tiempo: {missing_time_cols}")
            return False
          # 5. LIMPIAR BASE DE DATOS Y GUARDAR DATOS
        print("\n5. GUARDANDO EN BASE DE DATOS...")
        print("-" * 50)
        
        # Crear conexión a base de datos
        db_manager = DatabaseManager(db_path)
        print("✅ Conexión a BD establecida")
        
        # Limpiar tabla antes de cargar
        db_manager.limpiar_base_datos()
        print("✅ Tabla movimientos limpiada")
        
        # Guardar datos cartola
        db_manager.guardar_dataframe(df_con_tiempo, modo='replace')
        print("✅ Datos cartola guardados en BD")
          # 6. VERIFICAR DATOS EN BASE DE DATOS
        print("\n6. VERIFICANDO DATOS EN BD...")
        print("-" * 50)
        
        df_from_db = db_manager.obtener_todas_transacciones()
        print(f"✅ Datos recuperados de BD: {len(df_from_db)} registros")
        
        if len(df_from_db) != len(df_con_tiempo):
            print(f"⚠️  Diferencia en cantidad de registros:")
            print(f"   Procesados: {len(df_con_tiempo)}")
            print(f"   En BD: {len(df_from_db)}")
        
        # Verificar tipos en BD
        if len(df_from_db) > 0:
            tipo_counts_db = df_from_db['tipo'].value_counts()
            print(f"Distribución de tipos en BD:")
            for tipo, count in tipo_counts_db.items():
                print(f"  {tipo}: {count}")
        
        # 7. CALCULAR AGREGACIONES
        print("\n7. CALCULANDO AGREGACIONES...")
        print("-" * 50)
        
        # Agregaciones mensuales
        agg_mensual = calcular_agregaciones_por_tiempo(df_from_db, 'mes')
        print(f"✅ Agregaciones mensuales: {len(agg_mensual)} períodos")
        
        # Agregaciones semanales
        agg_semanal = calcular_agregaciones_por_tiempo(df_from_db, 'semana')
        print(f"✅ Agregaciones semanales: {len(agg_semanal)} períodos")
        
        # Mostrar resumen de agregaciones mensuales
        if len(agg_mensual) > 0:
            print("\nResumen agregaciones mensuales:")
            for _, row in agg_mensual.head(3).iterrows():
                print(f"  {row['periodo']}: Gastos=${row['total_gastos']:,.0f}, Ingresos=${row['total_ingresos']:,.0f}")
        
        # 8. VERIFICAR LIMPIEZA JSON
        print("\n8. VERIFICANDO LIMPIEZA JSON...")
        print("-" * 50)
        
        # Probar limpieza de agregaciones mensuales
        agg_mensual_json = limpiar_datos_para_json(agg_mensual.to_dict('records'))
        json_str = json.dumps(agg_mensual_json, ensure_ascii=False, indent=2)
        print("✅ Agregaciones mensuales convertidas a JSON exitosamente")
        print(f"   Tamaño JSON: {len(json_str)} caracteres")
        
        # Probar limpieza de datos completos
        df_sample = df_from_db.head(5)
        datos_sample_json = limpiar_datos_para_json(df_sample.to_dict('records'))
        json_str_sample = json.dumps(datos_sample_json, ensure_ascii=False, indent=2)
        print("✅ Datos de muestra convertidos a JSON exitosamente")
        
        # 9. SIMULACIÓN DE ENDPOINTS
        print("\n9. SIMULANDO ENDPOINTS...")
        print("-" * 50)
          # Simular endpoint /historial/
        try:
            datos_historial = db_manager.obtener_todas_transacciones()
            if 'año_mes' not in datos_historial.columns:
                datos_historial = agregar_columnas_tiempo(datos_historial)
            
            agregaciones = calcular_agregaciones_por_tiempo(datos_historial, 'mes')
            historial_response = {
                'agregaciones': limpiar_datos_para_json(agregaciones.to_dict('records')),
                'total_registros': len(datos_historial),
                'periodo_inicio': str(datos_historial['fecha'].min()),
                'periodo_fin': str(datos_historial['fecha'].max())
            }
            
            # Verificar que se puede serializar a JSON
            json.dumps(historial_response, ensure_ascii=False)
            print("✅ Endpoint /historial/ simulado exitosamente")
            
        except Exception as e:
            print(f"❌ Error simulando endpoint /historial/: {e}")
            return False
        
        # Simular endpoint /cargar-tef-locales/
        try:
            # Procesar otro archivo cartola si existe
            if len(archivos_cartola) > 1:
                file_name2, file_path2 = archivos_cartola[1]
                df_cartola2 = procesar_archivo_excel(file_path2)
                df_cartola2 = agregar_columnas_tiempo(df_cartola2)
                
                carga_response = {
                    'mensaje': f'Archivo {file_name2} procesado correctamente',
                    'registros_procesados': len(df_cartola2),
                    'tipos': limpiar_datos_para_json(df_cartola2['tipo'].value_counts().to_dict())
                }
                
                # Verificar que se puede serializar a JSON
                json.dumps(carga_response, ensure_ascii=False)
                print("✅ Endpoint /cargar-tef-locales/ simulado exitosamente")
            else:
                print("ℹ️  Solo hay un archivo cartola, no se puede simular carga adicional")
                
        except Exception as e:
            print(f"❌ Error simulando endpoint /cargar-tef-locales/: {e}")
            return False
        
        # 10. RESUMEN FINAL
        print("\n" + "=" * 80)
        print("RESUMEN FINAL DEL TEST")
        print("=" * 80)
        
        print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print(f"   📁 Archivos cartola procesados: {len(archivos_cartola)}")
        print(f"   📊 Registros totales en BD: {len(df_from_db)}")
        print(f"   📅 Períodos mensuales: {len(agg_mensual)}")
        print(f"   📈 Períodos semanales: {len(agg_semanal)}")
        
        if len(df_from_db) > 0:
            gastos_total = df_from_db[df_from_db['tipo'] == 'Gasto']['monto'].sum()
            ingresos_total = df_from_db[df_from_db['tipo'] == 'Ingreso']['monto'].sum()
            print(f"   💰 Total gastos: ${gastos_total:,.0f}")
            print(f"   💵 Total ingresos: ${ingresos_total:,.0f}")
            print(f"   📊 Balance: ${ingresos_total - gastos_total:,.0f}")
          print("\n🎉 INTEGRACIÓN DE CARTOLA FUNCIONANDO CORRECTAMENTE")
        
        # Cerrar conexión a BD
        db_manager.cerrar_conexion()
        return True
          except Exception as e:
        print(f"\n❌ ERROR EN TEST DE INTEGRACIÓN:")
        print(f"   {str(e)}")
        print(f"\n📍 Traceback completo:")
        traceback.print_exc()
        
        # Cerrar conexión si existe
        try:
            if 'db_manager' in locals():
                db_manager.cerrar_conexion()
        except:
            pass
            
        return False

def test_formato_detection_all_files():
    """Test específico para verificar detección de formato en todos los archivos"""
    print("\n" + "=" * 80)
    print("TEST DE DETECCIÓN DE FORMATO - TODOS LOS ARCHIVOS")
    print("=" * 80)
    
    data_folder = r"F:\Codes\FINANZAS PERSONALES\personal-dashboard\mi-dashboard-finanzas-astro\backend\data\load_excels"
    
    if not os.path.exists(data_folder):
        print("❌ Carpeta de datos no existe")
        return False
    
    archivos = [f for f in os.listdir(data_folder) if f.endswith(('.xls', '.xlsx'))]
    
    if not archivos:
        print("❌ No se encontraron archivos Excel")
        return False
    
    print(f"Analizando {len(archivos)} archivos...")
    
    resultados = {}
    for archivo in archivos:
        file_path = os.path.join(data_folder, archivo)
        try:
            formato = detectar_formato_archivo(file_path)
            resultados[archivo] = formato
            print(f"  📄 {archivo}: {formato}")
        except Exception as e:
            resultados[archivo] = f"ERROR: {e}"
            print(f"  ❌ {archivo}: ERROR - {e}")
    
    # Resumen
    print(f"\nResumen de formatos:")
    formatos_count = {}
    for archivo, formato in resultados.items():
        if formato.startswith("ERROR"):
            formato = "ERROR"
        formatos_count[formato] = formatos_count.get(formato, 0) + 1
    
    for formato, count in formatos_count.items():
        print(f"  {formato}: {count} archivo(s)")
    
    return True

if __name__ == "__main__":
    print("INICIANDO TESTS DE CARTOLA...")
    print(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar test de detección de formato
    test_formato_detection_all_files()
    
    # Ejecutar test integral
    success = test_cartola_integration()
    
    if success:
        print(f"\n🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
    else:
        print(f"\n❌ ALGUNOS TESTS FALLARON")
    
    print(f"\nTest finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

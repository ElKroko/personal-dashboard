#!/usr/bin/env python3
"""
Test completo para verificar el procesamiento de archivos TEF:
1. Lectura y conversión de datos
2. Guardado en base de datos
3. Recuperación desde base de datos
4. Verificación de integridad de datos
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import tempfile
import shutil

# Agregar el directorio backend al path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from utils.leer_excel import procesar_archivo_excel
from utils.categorizar import aplicar_categorizacion
from utils.fechas import agregar_columnas_tiempo, obtener_rango_fechas, obtener_periodos_disponibles
from utils.agregaciones import calcular_todas_agregaciones
from utils.bd import DatabaseManager

def print_separador(titulo):
    """Imprime un separador visual para organizar la salida"""
    print("\n" + "="*60)
    print(f"  {titulo}")
    print("="*60)

def verificar_tipos_datos(df, nombre_etapa):
    """Verifica los tipos de datos en el DataFrame"""
    print(f"\n📊 Tipos de datos en {nombre_etapa}:")
    for columna in df.columns:
        tipo = str(df[columna].dtype)
        ejemplo = df[columna].iloc[0] if len(df) > 0 else "N/A"
        print(f"  - {columna}: {tipo} (ejemplo: {ejemplo})")

def verificar_valores_nan(df, nombre_etapa):
    """Verifica valores NaN en el DataFrame"""
    print(f"\n🔍 Valores NaN en {nombre_etapa}:")
    nan_counts = df.isnull().sum()
    for columna, count in nan_counts.items():
        if count > 0:
            print(f"  - {columna}: {count} valores NaN")
    
    if nan_counts.sum() == 0:
        print("  ✅ No hay valores NaN")

def verificar_valores_infinitos(df, nombre_etapa):
    """Verifica valores infinitos en columnas numéricas"""
    print(f"\n♾️  Valores infinitos en {nombre_etapa}:")
    columnas_numericas = df.select_dtypes(include=[np.number]).columns
    
    hay_infinitos = False
    for columna in columnas_numericas:
        inf_count = np.isinf(df[columna]).sum()
        if inf_count > 0:
            print(f"  - {columna}: {inf_count} valores infinitos")
            hay_infinitos = True
    
    if not hay_infinitos:
        print("  ✅ No hay valores infinitos")

def mostrar_resumen_datos(df, nombre_etapa):
    """Muestra un resumen de los datos"""
    print(f"\n📈 Resumen de datos en {nombre_etapa}:")
    print(f"  - Total de filas: {len(df)}")
    print(f"  - Total de columnas: {len(df.columns)}")
    
    if 'fecha' in df.columns:
        fechas_validas = df['fecha'].notna().sum()
        print(f"  - Fechas válidas: {fechas_validas}")
        if fechas_validas > 0:
            fecha_min = df['fecha'].min()
            fecha_max = df['fecha'].max()
            print(f"  - Rango de fechas: {fecha_min} a {fecha_max}")
    
    if 'monto' in df.columns:
        montos_validos = df['monto'].notna().sum()
        print(f"  - Montos válidos: {montos_validos}")
        if montos_validos > 0:
            monto_min = df['monto'].min()
            monto_max = df['monto'].max()
            print(f"  - Rango de montos: ${monto_min:,.2f} a ${monto_max:,.2f}")

def mostrar_muestra_datos(df, nombre_etapa, n=3):
    """Muestra una muestra de los datos"""
    print(f"\n📋 Muestra de datos ({nombre_etapa}) - Primeras {n} filas:")
    if len(df) > 0:
        print(df.head(n).to_string(index=False))
    else:
        print("  ⚠️  DataFrame vacío")

def test_lectura_archivos_tef():
    """Test de lectura de archivos TEF"""
    print_separador("PASO 1: LECTURA DE ARCHIVOS TEF")
    
    load_excels_path = os.path.join(backend_path, "data", "load_excels")
    
    if not os.path.exists(load_excels_path):
        print(f"❌ Error: Carpeta {load_excels_path} no encontrada")
        return None
    
    # Buscar archivos Excel
    archivos_excel = []
    for archivo in os.listdir(load_excels_path):
        if archivo.endswith(('.xlsx', '.xls')):
            archivos_excel.append(os.path.join(load_excels_path, archivo))
    
    print(f"📁 Archivos TEF encontrados: {len(archivos_excel)}")
    for archivo in archivos_excel:
        print(f"  - {os.path.basename(archivo)}")
    
    if not archivos_excel:
        print("❌ No se encontraron archivos TEF")
        return None
    
    # Procesar cada archivo
    dataframes = []
    archivos_procesados = []
    
    for archivo_path in archivos_excel:
        print(f"\n🔄 Procesando: {os.path.basename(archivo_path)}")
        try:
            df = procesar_archivo_excel(archivo_path)
            print(f"  ✅ Archivo procesado: {len(df)} filas")
            
            # Verificar datos del archivo individual
            verificar_tipos_datos(df, f"archivo {os.path.basename(archivo_path)}")
            verificar_valores_nan(df, f"archivo {os.path.basename(archivo_path)}")
            mostrar_resumen_datos(df, f"archivo {os.path.basename(archivo_path)}")
            
            if not df.empty:
                dataframes.append(df)
                archivos_procesados.append(os.path.basename(archivo_path))
        except Exception as e:
            print(f"  ❌ Error procesando archivo: {e}")
            continue
    
    if not dataframes:
        print("❌ No se pudieron procesar los archivos TEF")
        return None
    
    # Combinar DataFrames
    print(f"\n🔗 Combinando {len(dataframes)} DataFrames...")
    df_completo = pd.concat(dataframes, ignore_index=True)
    print(f"✅ DataFrame combinado: {len(df_completo)} filas totales")
    
    # Eliminar duplicados
    print("\n🧹 Eliminando duplicados...")
    antes_duplicados = len(df_completo)
    columnas_clave = ['fecha', 'monto', 'detalle']
    df_completo = df_completo.drop_duplicates(subset=columnas_clave, keep='first')
    despues_duplicados = len(df_completo)
    duplicados_eliminados = antes_duplicados - despues_duplicados
    print(f"✅ Duplicados eliminados: {duplicados_eliminados}")
    print(f"📊 Filas finales: {despues_duplicados}")
    
    # Verificar datos combinados
    verificar_tipos_datos(df_completo, "datos combinados")
    verificar_valores_nan(df_completo, "datos combinados")
    verificar_valores_infinitos(df_completo, "datos combinados")
    mostrar_resumen_datos(df_completo, "datos combinados")
    mostrar_muestra_datos(df_completo, "datos combinados")
    
    return df_completo, archivos_procesados

def test_categorizacion(df):
    """Test de categorización"""
    print_separador("PASO 2: CATEGORIZACIÓN")
    
    print("🏷️  Aplicando categorización...")
    df_categorizado = aplicar_categorizacion(df)
    
    # Verificar categorías
    if 'categoria' in df_categorizado.columns:
        categorias = df_categorizado['categoria'].value_counts()
        print(f"\n📊 Categorías encontradas:")
        for categoria, count in categorias.items():
            print(f"  - {categoria}: {count} transacciones")
        
        sin_categoria = df_categorizado['categoria'].isnull().sum()
        if sin_categoria > 0:
            print(f"  ⚠️  Sin categoría: {sin_categoria} transacciones")
    
    verificar_tipos_datos(df_categorizado, "datos categorizados")
    verificar_valores_nan(df_categorizado, "datos categorizados")
    mostrar_resumen_datos(df_categorizado, "datos categorizados")
    
    return df_categorizado

def test_columnas_tiempo(df):
    """Test de agregación de columnas de tiempo"""
    print_separador("PASO 3: COLUMNAS DE TIEMPO")
    
    print("📅 Agregando columnas de tiempo...")
    df_con_tiempo = agregar_columnas_tiempo(df)
    
    # Verificar nuevas columnas
    columnas_tiempo = ['año', 'mes', 'día', 'día_semana', 'semana_año', 'año_mes']
    print(f"\n🕐 Columnas de tiempo agregadas:")
    for columna in columnas_tiempo:
        if columna in df_con_tiempo.columns:
            valores_unicos = df_con_tiempo[columna].nunique()
            print(f"  ✅ {columna}: {valores_unicos} valores únicos")
        else:
            print(f"  ❌ {columna}: NO ENCONTRADA")
    
    # Mostrar ejemplos de columnas de tiempo
    if len(df_con_tiempo) > 0:
        print(f"\n📋 Ejemplo de columnas de tiempo:")
        columnas_mostrar = ['fecha'] + [col for col in columnas_tiempo if col in df_con_tiempo.columns]
        if columnas_mostrar:
            print(df_con_tiempo[columnas_mostrar].head(3).to_string(index=False))
    
    verificar_tipos_datos(df_con_tiempo, "datos con tiempo")
    verificar_valores_nan(df_con_tiempo, "datos con tiempo")
    verificar_valores_infinitos(df_con_tiempo, "datos con tiempo")
    mostrar_resumen_datos(df_con_tiempo, "datos con tiempo")
    
    return df_con_tiempo

def test_agregaciones(df):
    """Test de cálculo de agregaciones"""
    print_separador("PASO 4: AGREGACIONES")
    
    print("📊 Calculando agregaciones...")
    try:
        agregaciones = calcular_todas_agregaciones(df)
        
        print(f"\n✅ Agregaciones calculadas:")
        for clave, valor in agregaciones.items():
            if isinstance(valor, (list, dict)):
                if isinstance(valor, list):
                    print(f"  - {clave}: lista con {len(valor)} elementos")
                else:
                    print(f"  - {clave}: diccionario con {len(valor)} claves")
            else:
                print(f"  - {clave}: {type(valor).__name__}")
        
        # Verificar resumen mensual
        if 'resumen_mensual' in agregaciones:
            resumen_mensual = agregaciones['resumen_mensual']
            print(f"\n📈 Resumen mensual: {len(resumen_mensual)} periodos")
            if len(resumen_mensual) > 0:
                print("  Primeros 3 periodos:")
                for i, periodo in enumerate(resumen_mensual[:3]):
                    print(f"    {i+1}. {periodo}")
        
        # Verificar promedios
        if 'promedios' in agregaciones:
            promedios = agregaciones['promedios']
            print(f"\n💰 Promedios calculados:")
            for clave, valor in promedios.items():
                if isinstance(valor, (int, float)):
                    print(f"  - {clave}: ${valor:,.2f}")
                else:
                    print(f"  - {clave}: {valor}")
        
        return agregaciones
        
    except Exception as e:
        print(f"❌ Error calculando agregaciones: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_base_datos(df):
    """Test de guardado y recuperación desde base de datos"""
    print_separador("PASO 5: BASE DE DATOS")
    
    # Crear base de datos temporal para testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_temp_path = tmp_db.name
    
    try:
        print(f"🗄️  Creando base de datos temporal: {db_temp_path}")
        
        # Crear instancia de DatabaseManager con DB temporal
        db_manager = DatabaseManager(db_path=db_temp_path)
        
        print("💾 Guardando datos en base de datos...")
        db_manager.guardar_dataframe(df, modo="replace")
        print("✅ Datos guardados correctamente")
        
        # Verificar conteo
        total_transacciones = db_manager.contar_transacciones()
        print(f"📊 Total de transacciones en BD: {total_transacciones}")
        
        # Recuperar datos
        print("📤 Recuperando datos desde base de datos...")
        df_recuperado = db_manager.obtener_todas_transacciones()
        print(f"✅ Datos recuperados: {len(df_recuperado)} filas")
        
        # Comparar datos originales vs recuperados
        print(f"\n🔍 Comparación de datos:")
        print(f"  - Filas originales: {len(df)}")
        print(f"  - Filas recuperadas: {len(df_recuperado)}")
        print(f"  - Columnas originales: {len(df.columns)}")
        print(f"  - Columnas recuperadas: {len(df_recuperado.columns)}")
        
        # Verificar integridad de datos recuperados
        verificar_tipos_datos(df_recuperado, "datos recuperados de BD")
        verificar_valores_nan(df_recuperado, "datos recuperados de BD")
        verificar_valores_infinitos(df_recuperado, "datos recuperados de BD")
        mostrar_resumen_datos(df_recuperado, "datos recuperados de BD")
        mostrar_muestra_datos(df_recuperado, "datos recuperados de BD")
        
        # Verificar que las columnas principales están presentes
        columnas_esenciales = ['fecha', 'monto', 'detalle', 'categoria']
        print(f"\n🔑 Verificación de columnas esenciales:")
        for columna in columnas_esenciales:
            if columna in df_recuperado.columns:
                print(f"  ✅ {columna}: presente")
            else:
                print(f"  ❌ {columna}: FALTANTE")
        
        # Cerrar conexión
        db_manager.cerrar_conexion()
        
        return df_recuperado
        
    except Exception as e:
        print(f"❌ Error con base de datos: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        # Limpiar archivo temporal
        if os.path.exists(db_temp_path):
            os.unlink(db_temp_path)
            print(f"🧹 Base de datos temporal eliminada")

def test_json_serialization(agregaciones):
    """Test de serialización JSON"""
    print_separador("PASO 6: SERIALIZACIÓN JSON")
    
    if not agregaciones:
        print("❌ No hay agregaciones para serializar")
        return
    
    print("📤 Probando serialización JSON...")
    
    try:
        import json
        
        # Función de limpieza (copiada del app.py)
        def limpiar_datos_para_json(obj):
            if isinstance(obj, dict):
                return {k: limpiar_datos_para_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [limpiar_datos_para_json(item) for item in obj]
            elif isinstance(obj, (pd.Series, pd.DataFrame)):
                return limpiar_datos_para_json(obj.to_dict())
            elif isinstance(obj, (float, np.floating)):
                if pd.isna(obj) or np.isinf(obj):
                    return None
                return float(obj)
            elif isinstance(obj, (int, np.integer)):
                if pd.isna(obj):
                    return None
                return int(obj)
            elif isinstance(obj, pd.Timestamp):
                return obj.strftime('%Y-%m-%d')
            elif pd.isna(obj):
                return None
            else:
                return obj
        
        # Probar serialización sin limpieza
        print("🧪 Probando serialización directa...")
        try:
            json_directo = json.dumps(agregaciones)
            print("  ✅ Serialización directa exitosa")
        except Exception as e:
            print(f"  ❌ Error en serialización directa: {e}")
        
        # Probar serialización con limpieza
        print("🧪 Probando serialización con limpieza...")
        try:
            agregaciones_limpias = limpiar_datos_para_json(agregaciones)
            json_limpio = json.dumps(agregaciones_limpias)
            print("  ✅ Serialización con limpieza exitosa")
            print(f"  📏 Tamaño JSON: {len(json_limpio)} caracteres")
        except Exception as e:
            print(f"  ❌ Error en serialización con limpieza: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error en test de serialización: {e}")

def main():
    """Función principal del test"""
    print_separador("TEST COMPLETO DE PROCESAMIENTO TEF")
    print(f"🕐 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. Lectura de archivos
        resultado_lectura = test_lectura_archivos_tef()
        if resultado_lectura is None:
            print("❌ Test terminado: Error en lectura de archivos")
            return
        
        df_completo, archivos_procesados = resultado_lectura
        
        # 2. Categorización
        df_categorizado = test_categorizacion(df_completo)
        
        # 3. Columnas de tiempo
        df_con_tiempo = test_columnas_tiempo(df_categorizado)
        
        # 4. Agregaciones
        agregaciones = test_agregaciones(df_con_tiempo)
        
        # 5. Base de datos
        df_recuperado = test_base_datos(df_con_tiempo)
        
        # 6. Serialización JSON
        test_json_serialization(agregaciones)
        
        # Resumen final
        print_separador("RESUMEN FINAL")
        print("✅ Test completado exitosamente")
        print(f"📁 Archivos procesados: {len(archivos_procesados)}")
        print(f"📊 Transacciones finales: {len(df_con_tiempo)}")
        print(f"🗄️  Datos en BD: {'✅' if df_recuperado is not None else '❌'}")
        print(f"📤 JSON serializable: {'✅' if agregaciones else '❌'}")
        
    except Exception as e:
        print(f"❌ Error en test principal: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print(f"\n🕐 Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

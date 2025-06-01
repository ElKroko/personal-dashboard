#!/usr/bin/env python3
"""
Test script for processing real TEF bank files with the enhanced integration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.leer_excel import cargar_y_limpiar_tef_cartola
from utils.categorizar import aplicar_categorizacion
from utils.fechas import agregar_columnas_tiempo
from utils.agregaciones import calcular_todas_agregaciones
import pandas as pd
import glob

def test_real_tef_files():
    """Test with real TEF files found in the data directory"""
    print("=== TEST CON ARCHIVOS TEF REALES ===")
    
    data_dir = "backend/data/load_excels"
    tef_files = glob.glob(os.path.join(data_dir, "tef-cartola*.xlsx"))
    
    if not tef_files:
        print("❌ No se encontraron archivos TEF en el directorio de datos")
        return
    
    print(f"✅ Encontrados {len(tef_files)} archivos TEF:")
    for file in tef_files:
        print(f"   - {os.path.basename(file)}")
    
    # Test with the first file
    test_file = tef_files[0]
    print(f"\n🔍 Procesando archivo: {os.path.basename(test_file)}")
    
    try:
        # 1. Load and process TEF data
        print("1. Cargando y procesando datos TEF...")
        df = cargar_y_limpiar_tef_cartola(test_file)
        print(f"   - Filas procesadas: {len(df)}")
        print(f"   - Columnas: {list(df.columns)}")
        
        # 2. Show data sample
        print("\n2. Muestra de datos procesados:")
        print(df[['fecha', 'detalle', 'monto', 'tipo']].head())
        
        # 3. Apply categorization
        print("\n3. Aplicando categorización...")
        df = aplicar_categorizacion(df)
        categories = df['categoria'].unique()
        print(f"   - Categorías encontradas: {categories}")
        
        # 4. Add time information
        print("\n4. Agregando información de fecha...")
        df = agregar_columnas_tiempo(df)
        time_columns = [col for col in df.columns if col in ['año', 'mes', 'dia', 'semana', 'dia_semana', 'año_mes', 'año_semana']]
        print(f"   - Nuevas columnas de fecha: {time_columns}")
        
        # 5. Category summary
        print("\n5. Resumen de categorías:")
        category_summary = df.groupby(['categoria', 'tipo']).agg({
            'monto': ['count', 'sum']
        })
        print(category_summary)
        
        # 6. Calculate statistics
        print("\n6. Calculando estadísticas...")
        total_ingresos = df[df['tipo'] == 'Ingreso']['monto'].sum()
        total_gastos = df[df['tipo'] == 'Gasto']['monto'].sum()
        balance = total_ingresos - total_gastos
        
        print(f"   - Total ingresos: ${total_ingresos:,.0f}")
        print(f"   - Total gastos: ${total_gastos:,.0f}")
        print(f"   - Balance: ${balance:,.0f}")
        
        # 7. Test aggregations
        print("\n7. Verificando agregaciones completas...")
        agregaciones = calcular_todas_agregaciones(df)
        for key, data in agregaciones.items():
            if hasattr(data, '__len__'):
                print(f"   - {key}: {len(data)} registros")
            else:
                print(f"   - {key}: {data}")
        
        # 8. Date range and transaction types
        print("\n8. Análisis de datos:")
        print(f"   - Rango de fechas: {df['fecha'].min()} a {df['fecha'].max()}")
        print(f"   - Tipos de transacción: {df['tipo'].value_counts().to_dict()}")
        
        # 9. Top categories by amount
        print("\n9. Top 5 categorías por monto:")
        top_categories = df.groupby('categoria')['monto'].sum().sort_values(ascending=False).head()
        for categoria, monto in top_categories.items():
            print(f"   - {categoria}: ${monto:,.0f}")
        
        print("\n✅ PROCESAMIENTO DE ARCHIVO TEF REAL COMPLETADO EXITOSAMENTE")
        
        # Test with all files for summary
        print(f"\n🔍 Procesando todos los archivos TEF ({len(tef_files)} archivos)...")
        all_data = []
        
        for file in tef_files:
            try:
                df_file = cargar_y_limpiar_tef_cartola(file)
                df_file = aplicar_categorizacion(df_file)
                df_file = agregar_columnas_tiempo(df_file)
                df_file['archivo'] = os.path.basename(file)
                all_data.append(df_file)
                print(f"   ✅ {os.path.basename(file)}: {len(df_file)} transacciones")
            except Exception as e:
                print(f"   ❌ {os.path.basename(file)}: Error - {str(e)}")
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"\n📊 RESUMEN COMPLETO - {len(combined_df)} transacciones totales:")
            
            total_ingresos_all = combined_df[combined_df['tipo'] == 'Ingreso']['monto'].sum()
            total_gastos_all = combined_df[combined_df['tipo'] == 'Gasto']['monto'].sum()
            balance_all = total_ingresos_all - total_gastos_all
            
            print(f"   - Total ingresos: ${total_ingresos_all:,.0f}")
            print(f"   - Total gastos: ${total_gastos_all:,.0f}")
            print(f"   - Balance total: ${balance_all:,.0f}")
            
            print("\n📈 Top categorías (todos los archivos):")
            top_all = combined_df.groupby('categoria')['monto'].sum().sort_values(ascending=False).head()
            for categoria, monto in top_all.items():
                print(f"   - {categoria}: ${monto:,.0f}")
        
    except Exception as e:
        print(f"❌ Error procesando archivo TEF: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_tef_files()

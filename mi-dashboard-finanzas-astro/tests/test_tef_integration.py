# Test de integración de la funcionalidad TEF del banco
# filepath: f:\Codes\FINANZAS PERSONALES\personal-dashboard\mi-dashboard-finanzas-astro\test_tef_integration.py

import pandas as pd
import sys
import os

# Agregar el directorio backend al path para importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.leer_excel import cargar_y_limpiar_tef_cartola, procesar_archivo_excel
from utils.categorizar import aplicar_categorizacion, obtener_resumen_categorias
from utils.fechas import agregar_columnas_tiempo
from utils.agregaciones import calcular_todas_agregaciones

def crear_datos_tef_ejemplo():
    """
    Crea un DataFrame de ejemplo simulando datos de un archivo TEF del banco
    con el formato exacto que espera la función de procesamiento
    """
    datos_ejemplo = {
        'Fecha': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-20'],
        'Origen': ['MI CUENTA CORRIENTE', 'MI CUENTA CORRIENTE', 'MI CUENTA CORRIENTE', 'MI CUENTA CORRIENTE', 'MI CUENTA CORRIENTE'],
        'Nombre Destino': ['SUPERMERCADO JUMBO', 'GASOLINERA COPEC', 'MARIA GONZALEZ', 'UNIVERSIDAD DE CHILE', 'BANCO CHILE'],
        'Rut Destino': ['96.500.760-0', '99.300.000-6', '12.345.678-9', '60.910.000-1', '97.004.000-5'],
        'Banco Destino': ['BANCO SANTANDER', 'BANCO ESTADO', 'BANCO CHILE', 'BANCO BCI', 'BANCO CHILE'],
        'Tipo de Cuenta': ['CUENTA CORRIENTE', 'CUENTA CORRIENTE', 'CUENTA VISTA', 'CUENTA CORRIENTE', 'CUENTA CORRIENTE'],
        'N Cuenta Destino': ['123456789', '987654321', '456789123', '789123456', '321654987'],
        'Monto': [45000, 35000, 50000, 120000, 15000],
        'Estado': ['PROCESADA', 'PROCESADA', 'PROCESADA', 'PROCESADA', 'PROCESADA'],
        'Canal': ['WEB', 'MOBILE', 'WEB', 'WEB', 'ATM'],
        'Id Transacción': ['TRX001', 'TRX002', 'TRX003', 'TRX004', 'TRX005'],
        'Comentario': ['COMPRA SUPERMERCADO', 'COMBUSTIBLE', 'PRESTAMO FAMILIAR', 'PAGO MATRICULA', 'COMISION MANTENCION']
    }
    
    # Crear las primeras 11 filas vacías (simulando cabeceras del banco)
    filas_vacias = []
    for i in range(11):
        fila_vacia = {}
        for col in datos_ejemplo.keys():
            fila_vacia[col] = '' if i < 10 else col  # La fila 11 (índice 10) contiene los headers
        filas_vacias.append(fila_vacia)
    
    # Crear DataFrame con las filas vacías primero
    df_vacio = pd.DataFrame(filas_vacias)
    
    # Agregar los datos reales
    df_datos = pd.DataFrame(datos_ejemplo)
    
    # Combinar para simular el formato real del banco (11 filas vacías + datos)
    df_completo = pd.concat([df_vacio, df_datos], ignore_index=True)
    
    return df_completo

def test_procesamiento_tef():
    """
    Prueba el procesamiento completo de un archivo TEF simulado
    """
    print("=== TEST DE INTEGRACIÓN TEF BANCARIO ===\n")
    
    # 1. Crear datos de ejemplo
    print("1. Creando datos de ejemplo TEF...")
    df_raw = crear_datos_tef_ejemplo()
    
    # Guardar en un archivo temporal para probar la función de lectura
    archivo_temp = "temp_tef_ejemplo.xlsx"
    df_raw.to_excel(archivo_temp, index=False)
    
    try:
        # 2. Procesar con la función de carga TEF
        print("2. Procesando datos con función TEF...")
        df_tef = cargar_y_limpiar_tef_cartola(archivo_temp)
        print(f"   - Filas procesadas: {len(df_tef)}")
        print(f"   - Columnas: {list(df_tef.columns)}")
        
        # 3. Mostrar primeras filas procesadas
        print("\n3. Primeras filas procesadas:")
        print(df_tef[['fecha', 'detalle', 'monto', 'tipo']].head())
        
        # 4. Aplicar categorización
        print("\n4. Aplicando categorización...")
        df_categorizado = aplicar_categorizacion(df_tef)
        print(f"   - Categorías encontradas: {df_categorizado['categoria'].unique()}")
          # 5. Agregar información de fecha
        print("\n5. Agregando información de fecha...")
        df_fechas = agregar_columnas_tiempo(df_categorizado)
        print(f"   - Nuevas columnas de fecha: {[col for col in df_fechas.columns if col.startswith(('año', 'mes', 'dia', 'semana'))]}")
          # 6. Mostrar resumen de categorías
        print("\n6. Resumen de categorías:")
        resumen = obtener_resumen_categorias(df_fechas)
        print(resumen)
        
        # 7. Calcular estadísticas
        print("\n7. Calculando estadísticas...")
        stats = calcular_todas_agregaciones(df_fechas)
        # Extraer estadísticas básicas del resultado
        total_ingresos = df_fechas[df_fechas['tipo'] == 'Ingreso']['monto'].sum()
        total_gastos = df_fechas[df_fechas['tipo'] == 'Gasto']['monto'].sum()
        balance = total_ingresos - total_gastos
        promedio_diario = balance / len(df_fechas['fecha'].unique()) if len(df_fechas['fecha'].unique()) > 0 else 0
        
        print(f"   - Total ingresos: ${total_ingresos:,.0f}")
        print(f"   - Total gastos: ${total_gastos:,.0f}")
        print(f"   - Balance: ${balance:,.0f}")
        print(f"   - Promedio diario: ${promedio_diario:,.0f}")
        
        # 8. Verificar agregaciones completas
        print("\n8. Verificando agregaciones completas...")
        print(f"   - Resumen mensual: {len(stats['resumen_mensual'])} registros")
        print(f"   - Resumen semanal: {len(stats['resumen_semanal'])} registros")
        print(f"   - Saldo diario: {len(stats['saldo_diario'])} registros")
        print(f"   - Estado semanal: {stats['estado_semanal']['estado']}")
        
        print("\n✅ INTEGRACIÓN TEF COMPLETADA EXITOSAMENTE")
        
        # Mostrar DataFrame final
        print("\n9. DataFrame final (primeras 3 filas):")
        columnas_importantes = ['fecha', 'detalle', 'monto', 'tipo', 'categoria', 'nombre_destino', 'comentario']
        print(df_fechas[columnas_importantes].head(3).to_string())
        
    except Exception as e:
        print(f"❌ ERROR durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpiar archivo temporal
        if os.path.exists(archivo_temp):
            os.remove(archivo_temp)

if __name__ == "__main__":
    test_procesamiento_tef()

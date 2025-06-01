# Script para analizar datos TEF reales y mejorar la categorización
import pandas as pd
import os
from utils.leer_excel import cargar_y_limpiar_tef_cartola
from utils.categorizar import aplicar_categorizacion

def analizar_datos_tef():
    """Analiza los datos TEF reales para identificar transacciones sin categorizar"""
    
    # Directorio con los archivos TEF
    data_dir = "data/load_excels"
    archivos_tef = [f for f in os.listdir(data_dir) if f.endswith('.xlsx')]
    
    print(f"=== ANÁLISIS DE DATOS TEF REALES ===\n")
    print(f"Archivos encontrados: {len(archivos_tef)}")
    
    # Procesar todos los archivos TEF
    df_total = pd.DataFrame()
    
    for archivo in archivos_tef:
        print(f"\nProcesando: {archivo}")
        ruta_archivo = os.path.join(data_dir, archivo)
        
        try:
            # Cargar y limpiar datos TEF
            df = cargar_y_limpiar_tef_cartola(ruta_archivo)
            print(f"  - Transacciones: {len(df)}")
            
            # Aplicar categorización
            df = aplicar_categorizacion(df)
            
            # Agregar al DataFrame total
            df_total = pd.concat([df_total, df], ignore_index=True)
            
        except Exception as e:
            print(f"  - Error: {e}")
    
    if df_total.empty:
        print("No se pudieron procesar datos")
        return
    
    print(f"\n=== RESUMEN TOTAL ===")
    print(f"Total transacciones: {len(df_total)}")
    print(f"Rango de fechas: {df_total['fecha'].min()} a {df_total['fecha'].max()}")
    
    # Analizar categorización
    print(f"\n=== ANÁLISIS DE CATEGORIZACIÓN ===")
    categorias = df_total['categoria'].value_counts()
    print("Distribución por categorías:")
    for categoria, cantidad in categorias.items():
        porcentaje = (cantidad / len(df_total)) * 100
        print(f"  {categoria}: {cantidad} ({porcentaje:.1f}%)")
    
    # Analizar transacciones sin categorizar
    sin_categorizar = df_total[df_total['categoria'] == 'Sin categorizar']
    
    if len(sin_categorizar) > 0:
        print(f"\n=== TRANSACCIONES SIN CATEGORIZAR ({len(sin_categorizar)}) ===")
        
        # Mostrar ejemplos de detalles únicos sin categorizar
        detalles_unicos = sin_categorizar['detalle'].value_counts().head(20)
        print("\nDetalles más frecuentes sin categorizar:")
        for detalle, cantidad in detalles_unicos.items():
            print(f"  '{detalle}': {cantidad} veces")
        
        # Mostrar nombres de destino únicos sin categorizar
        print("\nNombres de destino únicos sin categorizar:")
        nombres_unicos = sin_categorizar['nombre_destino'].value_counts().head(15)
        for nombre, cantidad in nombres_unicos.items():
            print(f"  '{nombre}': {cantidad} veces")
        
        # Mostrar comentarios únicos sin categorizar
        print("\nComentarios únicos sin categorizar:")
        comentarios_unicos = sin_categorizar['comentario'].value_counts().head(15)
        for comentario, cantidad in comentarios_unicos.items():
            print(f"  '{comentario}': {cantidad} veces")
    
    # Análisis por tipo de transacción
    print(f"\n=== ANÁLISIS POR TIPO ===")
    tipos = df_total['tipo'].value_counts()
    for tipo, cantidad in tipos.items():
        porcentaje = (cantidad / len(df_total)) * 100
        monto_total = df_total[df_total['tipo'] == tipo]['monto'].sum()
        print(f"  {tipo}: {cantidad} transacciones ({porcentaje:.1f}%) - Total: ${monto_total:,.0f}")
    
    return df_total

if __name__ == "__main__":
    analizar_datos_tef()

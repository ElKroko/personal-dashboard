#!/usr/bin/env python3
"""
Analyze uncategorized transactions to improve categorization rules
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.leer_excel import cargar_y_limpiar_tef_cartola
from utils.categorizar import aplicar_categorizacion
import pandas as pd
import glob

def analyze_uncategorized():
    """Analyze uncategorized transactions to improve rules"""
    print("=== ANÁLISIS DE TRANSACCIONES SIN CATEGORIZAR ===")
    
    data_dir = "backend/data/load_excels"
    tef_files = glob.glob(os.path.join(data_dir, "tef-cartola*.xlsx"))
    
    all_data = []
    
    for file in tef_files:
        try:
            df_file = cargar_y_limpiar_tef_cartola(file)
            df_file = aplicar_categorizacion(df_file)
            df_file['archivo'] = os.path.basename(file)
            all_data.append(df_file)
        except Exception as e:
            print(f"Error procesando {file}: {e}")
    
    if not all_data:
        print("No se pudieron procesar archivos")
        return
    
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Find uncategorized transactions
    uncategorized = combined_df[combined_df['categoria'] == 'Sin categorizar']
    
    print(f"📊 Total transacciones: {len(combined_df)}")
    print(f"❌ Sin categorizar: {len(uncategorized)} ({len(uncategorized)/len(combined_df)*100:.1f}%)")
    
    if len(uncategorized) > 0:
        print("\n🔍 TRANSACCIONES SIN CATEGORIZAR:")
        print("="*80)
        
        for idx, row in uncategorized.iterrows():
            print(f"Archivo: {row['archivo']}")
            print(f"Fecha: {row['fecha']}")
            print(f"Detalle: {row['detalle']}")
            print(f"Nombre destino: {row['nombre_destino']}")
            print(f"Comentario: {row['comentario']}")
            print(f"Monto: ${row['monto']:,.0f}")
            print(f"Tipo: {row['tipo']}")
            print("-" * 80)
        
        # Analyze patterns
        print("\n📈 ANÁLISIS DE PATRONES:")
        
        # Most common words in detalle
        all_details = ' '.join(uncategorized['detalle'].fillna('').str.upper())
        words = all_details.split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        print("\n🔤 Palabras más frecuentes en detalles:")
        for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   - {word}: {freq} veces")
        
        # Most common destination names
        print("\n👤 Nombres de destino más frecuentes:")
        name_counts = uncategorized['nombre_destino'].value_counts().head(10)
        for name, count in name_counts.items():
            print(f"   - {name}: {count} veces")
        
        # Most common comments
        print("\n💬 Comentarios más frecuentes:")
        comment_counts = uncategorized['comentario'].fillna('Sin comentario').value_counts().head(10)
        for comment, count in comment_counts.items():
            print(f"   - {comment}: {count} veces")
    
    # Show categorized transactions summary
    categorized = combined_df[combined_df['categoria'] != 'Sin categorizar']
    print(f"\n✅ TRANSACCIONES CATEGORIZADAS: {len(categorized)}")
    
    print("\n📊 RESUMEN POR CATEGORÍA:")
    category_summary = categorized.groupby('categoria').agg({
        'monto': ['count', 'sum']
    }).round(0)
    print(category_summary)

if __name__ == "__main__":
    analyze_uncategorized()

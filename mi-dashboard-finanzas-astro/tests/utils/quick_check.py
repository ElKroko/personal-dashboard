import sys
import os
sys.path.append('backend')

from utils.leer_excel import cargar_y_limpiar_tef_cartola
from utils.categorizar import aplicar_categorizacion

df = cargar_y_limpiar_tef_cartola('backend/data/load_excels/tef-cartola (1).xlsx')
df = aplicar_categorizacion(df)

uncategorized = df[df['categoria'] == 'Sin categorizar']
print(f'Uncategorized transactions: {len(uncategorized)}')

if len(uncategorized) > 0:
    print('Details:')
    for idx, row in uncategorized.iterrows():
        print(f'- {row["nombre_destino"]} | ${row["monto"]:,.0f}')
        print(f'  Detalle: {row["detalle"]}')
        print(f'  Comentario: {row["comentario"]}')
        print('---')

import pandas as pd

def cargar_y_limpiar_tef_cartola(ruta_archivo: str) -> pd.DataFrame:
    """
    Lee el archivo Excel 'tef-cartola.xlsx' asumiendo que la cabecera comienza en la fila 12 (índice 11):
    - Elimina columnas vacías (Unnamed).
    - Renombra columnas a nombres más sencillos.
    - Convierte tipos (fecha a datetime, monto a numérico).
    - Limpia cadenas de texto.
    - Elimina filas sin fecha válida.
    """
    # 1. Leer con header en la fila 11
    df = pd.read_excel(ruta_archivo, header=11)

    # 2. Quitar columnas 'Unnamed'
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # 3. Renombrar columnas para estandarizar nombres
    df = df.rename(columns={
        'Fecha': 'fecha',
        'Origen': 'origen',
        'Nombre Destino': 'nombre_destino',
        'Rut Destino': 'rut_destino',
        'Banco Destino': 'banco_destino',
        'Tipo de Cuenta': 'tipo_cuenta',
        'N Cuenta Destino': 'cuenta_destino',
        'Monto': 'monto',
        'Estado': 'estado',
        'Canal': 'canal',
        'Id Transacción': 'id_transaccion',
        'Comentario': 'comentario'
    })

    # 4. Convertir tipos de columna
    df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
    df['monto'] = pd.to_numeric(df['monto'], errors='coerce').fillna(0.0)

    # Limpiar strings (quitar espacios sobrantes)
    campos_texto = [
        'origen', 'nombre_destino', 'rut_destino', 'banco_destino',
        'tipo_cuenta', 'cuenta_destino', 'estado', 'canal',
        'id_transaccion', 'comentario'
    ]
    for col in campos_texto:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 5. Eliminar filas sin fecha válida
    df = df.dropna(subset=['fecha'])
    return df

# Ejemplo de uso: cargar y mostrar las primeras filas
df_tef = cargar_y_limpiar_tef_cartola('/ruta/a/tu/tef-cartola.xlsx')
print(df_tef.head(10))

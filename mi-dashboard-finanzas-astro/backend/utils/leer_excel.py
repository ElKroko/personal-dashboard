import pandas as pd
from datetime import datetime
import io


def detectar_formato_archivo(archivo_path):
    """
    Detecta si el archivo es formato TEF (header en fila 11) o Cartola (header en fila 24)
    """
    try:
        # Leer sin header para examinar la estructura
        df_raw = pd.read_excel(archivo_path, header=None)
        
        # Verificar formato Cartola (fila 24 contiene headers específicos)
        if len(df_raw) > 24:
            fila_24 = df_raw.iloc[24].dropna().tolist()
            if any('Fecha' in str(cell) for cell in fila_24) and any('Descripción' in str(cell) for cell in fila_24):
                return 'cartola'
        
        # Verificar formato TEF (fila 11 contiene headers específicos)
        if len(df_raw) > 11:
            fila_11 = df_raw.iloc[11].dropna().tolist()
            if any('Fecha' in str(cell) for cell in fila_11) and any('Origen' in str(cell) for cell in fila_11):
                return 'tef'
        
        return 'generico'
    except:
        return 'generico'


def cargar_y_limpiar_cartola(archivo_path):
    """
    Lee archivos de cartola bancaria con header en fila 24 (B25):
    - Columnas: Fecha, Descripción, Canal o Sucursal, Cargos (PESOS), Abonos (PESOS), Saldo (PESOS)
    - Convierte tipos de datos y normaliza formato
    - Determina tipo de movimiento (Gasto/Ingreso) basado en Cargos/Abonos
    """
    # 1. Leer con header en la fila 24
    df = pd.read_excel(archivo_path, header=24)
    
    # 2. Quitar columnas 'Unnamed'
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # 3. Renombrar columnas para estandarizar nombres
    df = df.rename(columns={
        'Fecha': 'fecha',
        'Descripción': 'detalle',
        'Canal o Sucursal': 'canal',
        'Cargos (PESOS)': 'cargo',
        'Abonos (PESOS)': 'abono',
        'Saldo (PESOS)': 'saldo'
    })
    
    # 4. Convertir tipos de columna
    def parse_fecha_robusta(fecha_serie):
        """Parse fechas de manera robusta sin generar warnings"""
        if pd.api.types.is_datetime64_any_dtype(fecha_serie):
            return fecha_serie
        
        # Convertir a string si no lo es
        fecha_serie = fecha_serie.astype(str)
        
        # Para cartola, las fechas vienen en formato DD/MM
        # Necesitamos agregar el año actual
        from datetime import datetime
        año_actual = datetime.now().year
        
        # Procesar fecha por fecha
        fechas_procesadas = []
        for fecha_str in fecha_serie:
            if pd.isna(fecha_str) or fecha_str.strip() == '' or fecha_str == 'nan':
                fechas_procesadas.append(pd.NaT)
                continue
                
            try:
                # Si ya tiene año, usar como está
                if len(fecha_str.split('/')) == 3:
                    fechas_procesadas.append(pd.to_datetime(fecha_str, format='%d/%m/%Y'))
                # Si solo tiene día/mes, agregar año actual
                elif len(fecha_str.split('/')) == 2:
                    fecha_completa = f"{fecha_str}/{año_actual}"
                    fechas_procesadas.append(pd.to_datetime(fecha_completa, format='%d/%m/%Y'))
                else:
                    fechas_procesadas.append(pd.NaT)
            except:
                fechas_procesadas.append(pd.NaT)
        
        return pd.Series(fechas_procesadas, index=fecha_serie.index)
    
    df['fecha'] = parse_fecha_robusta(df['fecha'])
    
    # 5. Procesar montos - combinar cargos y abonos en una sola columna 'monto'
    df['cargo'] = pd.to_numeric(df['cargo'], errors='coerce').fillna(0.0)
    df['abono'] = pd.to_numeric(df['abono'], errors='coerce').fillna(0.0)
    
    # Crear columna monto y tipo basado en cargos/abonos
    def procesar_movimiento(row):
        if row['cargo'] > 0:
            return row['cargo'], 'Gasto'
        elif row['abono'] > 0:
            return row['abono'], 'Ingreso'
        else:
            return 0.0, 'Gasto'  # Default
    
    df[['monto', 'tipo']] = df.apply(lambda row: pd.Series(procesar_movimiento(row)), axis=1)
    
    # 6. Limpiar strings
    campos_texto = ['detalle', 'canal']
    for col in campos_texto:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # 7. Eliminar filas sin fecha válida o sin movimiento
    df = df.dropna(subset=['fecha'])
    df = df[df['monto'] > 0]  # Solo movimientos con monto
    
    # 8. Normalizar detalle
    df['detalle'] = df['detalle'].str.upper()
    
    # 9. Seleccionar solo las columnas estándar
    df = df[['fecha', 'detalle', 'monto', 'tipo', 'canal']].copy()
    
    return df


def cargar_y_limpiar_tef_cartola(archivo_path):
    """
    Lee el archivo Excel 'tef-cartola.xlsx' asumiendo que la cabecera comienza en la fila 12 (índice 11):
    - Elimina columnas vacías (Unnamed).
    - Renombra columnas a nombres más sencillos.
    - Convierte tipos (fecha a datetime, monto a numérico).
    - Limpia cadenas de texto.
    - Elimina filas sin fecha válida.
    - Determina tipo de movimiento (Gasto/Ingreso).
    """
    # 1. Leer con header en la fila 11
    df = pd.read_excel(archivo_path, header=11)

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
    })    # 4. Convertir tipos de columna
    def parse_fecha_robusta(fecha_serie):
        """Parse fechas de manera robusta sin generar warnings"""
        if pd.api.types.is_datetime64_any_dtype(fecha_serie):
            return fecha_serie
        
        # Convertir a string si no lo es
        fecha_serie = fecha_serie.astype(str)
        
        # Intentar parsing automático primero (sin dayfirst para evitar warnings)
        try:
            resultado = pd.to_datetime(fecha_serie, errors='coerce')
            if not resultado.isna().all():
                return resultado
        except:
            pass
        
        # Si eso falla, intentar formatos específicos
        formatos = [
            '%Y-%m-%d',   # 2024-01-15
            '%d/%m/%Y',   # 15/01/2024  
            '%m/%d/%Y',   # 01/15/2024
            '%Y/%m/%d',   # 2024/01/15
            '%d-%m-%Y',   # 15-01-2024
            '%Y%m%d',     # 20240115
        ]
        
        for formato in formatos:
            try:
                resultado = pd.to_datetime(fecha_serie, format=formato, errors='coerce')
                if not resultado.isna().all():
                    return resultado
            except:
                continue
        
        # Último recurso: usar dayfirst=False para evitar warnings
        return pd.to_datetime(fecha_serie, dayfirst=False, errors='coerce')
    
    df['fecha'] = parse_fecha_robusta(df['fecha'])
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
    
    # 6. Crear columna 'detalle' combinando información relevante
    def crear_detalle(row):
        partes = []
        if pd.notna(row.get('nombre_destino')) and str(row.get('nombre_destino')).strip() not in ['nan', '']:
            partes.append(str(row.get('nombre_destino')).strip())
        if pd.notna(row.get('comentario')) and str(row.get('comentario')).strip() not in ['nan', '']:
            partes.append(str(row.get('comentario')).strip())
        if pd.notna(row.get('banco_destino')) and str(row.get('banco_destino')).strip() not in ['nan', '']:
            partes.append(f"({str(row.get('banco_destino')).strip()})")
        
        detalle = " - ".join(partes) if partes else "Transferencia bancaria"
        return detalle.upper()
    
    df['detalle'] = df.apply(crear_detalle, axis=1)
    
    # 7. Determinar tipo de movimiento (Gasto/Ingreso)
    def determinar_tipo_movimiento(row):
        # Para TEF, normalmente son gastos (transferencias salientes)
        # Pero podemos usar heurísticas para detectar ingresos
        
        origen = str(row.get('origen', '')).upper()
        nombre_destino = str(row.get('nombre_destino', '')).upper()
        comentario = str(row.get('comentario', '')).upper()
        canal = str(row.get('canal', '')).upper()
        
        # Patrones que sugieren ingresos
        patrones_ingreso = [
            'SUELDO', 'SALARIO', 'NOMINA', 'HONORARIOS', 'REMUNERACION',
            'DEVOLUCION', 'REEMBOLSO', 'DEPOSITO', 'ABONO', 'CREDITO',
            'PENSION', 'JUBILACION', 'SUBSIDIO', 'BECA', 'PREMIO',
            'VENTA', 'COBRO', 'PAGO RECIBIDO', 'TRANSFERENCIA RECIBIDA'
        ]
        
        # Verificar en origen, destino y comentario
        texto_completo = f"{origen} {nombre_destino} {comentario}"
        
        for patron in patrones_ingreso:
            if patron in texto_completo:
                return 'Ingreso'
        
        # Si el origen contiene nuestro nombre/banco, podría ser un ingreso
        # (esto requeriría configuración del usuario en el futuro)
        
        # Por defecto, asumimos que es gasto (transferencia saliente)
        return 'Gasto'
    
    df['tipo'] = df.apply(determinar_tipo_movimiento, axis=1)
    
    return df


def leer_archivo_excel(archivo_path):
    """
    Función principal que detecta el tipo de archivo y aplica el procesamiento adecuado.
    Soporta archivos TEF, Cartola y Excel genéricos.
    """
    try:
        # Detectar formato automáticamente
        formato = detectar_formato_archivo(archivo_path)
        print(f"Formato detectado: {formato}")
        
        # Procesar según el formato detectado
        if formato == 'cartola':
            df = cargar_y_limpiar_cartola(archivo_path)
            if len(df) > 0:
                return df
        elif formato == 'tef':
            df = cargar_y_limpiar_tef_cartola(archivo_path)
            if len(df) > 0:
                return df
        
        # Formato genérico (original)
        df = pd.read_excel(archivo_path)
        
        # Renombrar columnas a nombres estándar
        column_mapping = {
            'Fecha Mov.': 'fecha',
            'Fecha': 'fecha', 
            'Descripción': 'detalle',
            'Descripcion': 'detalle',
            'Detalle': 'detalle',
            'Concepto': 'detalle',
            'Monto': 'monto',
            'Importe': 'monto',
            'Valor': 'monto',
            'Tipo': 'tipo',
            'Tipo Mov.': 'tipo',
            'Movimiento': 'tipo'
        }        
        # Aplicar renombrado si las columnas existen
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df.rename(columns={old_name: new_name}, inplace=True)
        
        # Asegurar que existe la columna 'detalle'
        if 'detalle' not in df.columns:
            # Buscar cualquier columna que pueda servir como descripción
            desc_columns = [col for col in df.columns if any(word in col.lower() 
                           for word in ['desc', 'concepto', 'detalle', 'movimiento'])]
            if desc_columns:
                df['detalle'] = df[desc_columns[0]]
            else:
                df['detalle'] = 'Transacción'
        
        return df
    except Exception as e:
        raise Exception(f"Error al leer archivo Excel: {str(e)}")


def limpiar_dataframe(df):
    """
    Función para limpiar y normalizar el DataFrame.
    Convierte tipos de datos y mapea valores.
    """
    # Hacer una copia para no modificar el original
    df_clean = df.copy()
    
    # Verificar que existan las columnas requeridas
    required_columns = ['fecha', 'detalle', 'monto', 'tipo']
    missing_columns = [col for col in required_columns if col not in df_clean.columns]
    
    if missing_columns:
        raise Exception(f"Faltan columnas requeridas: {missing_columns}")
    
    # Convertir fecha a datetime
    df_clean['fecha'] = pd.to_datetime(df_clean['fecha'], errors='coerce')
    
    # Convertir monto a numérico
    df_clean['monto'] = pd.to_numeric(df_clean['monto'], errors='coerce')
    
    # Mapear tipo de movimiento
    tipo_mapping = {
        'C': 'Ingreso',
        'CRÉDITO': 'Ingreso', 
        'CREDITO': 'Ingreso',
        'D': 'Gasto',
        'DÉBITO': 'Gasto',
        'DEBITO': 'Gasto'
    }
    
    # Aplicar mapeo de tipos
    df_clean['tipo'] = df_clean['tipo'].str.upper()
    df_clean['tipo'] = df_clean['tipo'].map(tipo_mapping).fillna(df_clean['tipo'])
    
    # Eliminar filas con valores nulos en campos críticos
    df_clean = df_clean.dropna(subset=['fecha', 'monto', 'tipo'])
    
    # Asegurar que el detalle no sea nulo
    df_clean['detalle'] = df_clean['detalle'].fillna('Sin descripción')
    
    # Convertir detalle a string y limpiar
    df_clean['detalle'] = df_clean['detalle'].astype(str).str.strip().str.upper()
    
    return df_clean


def procesar_archivo_excel(archivo_path):
    """
    Función principal que lee y limpia un archivo Excel.
    Retorna DataFrame procesado sin filas nulas en fecha, monto o tipo.
    """
    df = leer_archivo_excel(archivo_path)
    df_clean = limpiar_dataframe(df)
    
    return df_clean

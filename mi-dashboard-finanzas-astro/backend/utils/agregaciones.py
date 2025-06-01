import pandas as pd
from datetime import datetime, timedelta


def calcular_resumen_mensual(df):
    """
    Resumen mensual: agrupar por año y mes, sumar montos de ingresos por un lado 
    y gastos por otro, y calcular el neto (ingresos menos gastos).
    """
    if not all(col in df.columns for col in ['año', 'mes', 'tipo', 'monto']):
        raise Exception("El DataFrame debe contener las columnas: año, mes, tipo, monto")
    
    # Agrupar por año, mes y tipo
    resumen = df.groupby(['año', 'mes', 'tipo'])['monto'].sum().reset_index()
    
    # Pivotar para tener ingresos y gastos en columnas separadas
    resumen_pivot = resumen.pivot_table(
        index=['año', 'mes'], 
        columns='tipo', 
        values='monto', 
        fill_value=0
    ).reset_index()
      # Asegurar que existan las columnas de INGRESO y GASTO (mayúsculas)
    if 'INGRESO' not in resumen_pivot.columns:
        resumen_pivot['INGRESO'] = 0
    if 'GASTO' not in resumen_pivot.columns:
        resumen_pivot['GASTO'] = 0
    
    # Calcular neto (ingresos - gastos)
    resumen_pivot['neto'] = resumen_pivot['INGRESO'] - resumen_pivot['GASTO']
    
    # Renombrar columnas para consistencia
    resumen_pivot.columns.name = None
    resumen_pivot = resumen_pivot.rename(columns={
        'INGRESO': 'total_ingresos',
        'GASTO': 'total_gastos'
    })
    
    # Crear etiqueta año-mes para gráficos
    resumen_pivot['año_mes'] = resumen_pivot['año'].astype(str) + '-' + \
                               resumen_pivot['mes'].astype(str).str.zfill(2)
    
    return resumen_pivot.round(2)


def calcular_promedio_mensual(resumen_mensual):
    """
    Promedio mensual: a partir del resumen mensual, obtener el ingreso promedio 
    y el gasto promedio.
    """
    if resumen_mensual.empty:
        return {'ingreso_promedio': 0, 'gasto_promedio': 0}
    
    ingreso_promedio = resumen_mensual['total_ingresos'].mean()
    gasto_promedio = resumen_mensual['total_gastos'].mean()
    
    return {
        'ingreso_promedio': round(ingreso_promedio, 2),
        'gasto_promedio': round(gasto_promedio, 2)
    }


def calcular_gasto_diario_referencia(gasto_promedio_mensual):
    """
    Gasto diario de referencia: dividir el gasto promedio mensual entre 30 
    para obtener un "gasto diario promedio".
    """
    if gasto_promedio_mensual == 0:
        return 0
    
    return round(gasto_promedio_mensual / 30, 2)


def calcular_resumen_semanal(df):
    """
    Resumen semanal: agrupar por año y semana, calculando ingresos, gastos y neto.
    """
    if not all(col in df.columns for col in ['año', 'semana', 'tipo', 'monto']):
        raise Exception("El DataFrame debe contener las columnas: año, semana, tipo, monto")
    
    # Agrupar por año, semana y tipo
    resumen = df.groupby(['año', 'semana', 'tipo'])['monto'].sum().reset_index()
    
    # Pivotar para tener ingresos y gastos en columnas separadas
    resumen_pivot = resumen.pivot_table(
        index=['año', 'semana'], 
        columns='tipo', 
        values='monto', 
        fill_value=0
    ).reset_index()
      # Asegurar que existan las columnas de INGRESO y GASTO (mayúsculas)
    if 'INGRESO' not in resumen_pivot.columns:
        resumen_pivot['INGRESO'] = 0
    if 'GASTO' not in resumen_pivot.columns:
        resumen_pivot['GASTO'] = 0
    
    # Calcular neto
    resumen_pivot['neto'] = resumen_pivot['INGRESO'] - resumen_pivot['GASTO']
    
    # Renombrar columnas
    resumen_pivot.columns.name = None
    resumen_pivot = resumen_pivot.rename(columns={
        'Ingreso': 'total_ingresos',
        'Gasto': 'total_gastos'
    })
    
    # Crear etiqueta año-semana
    resumen_pivot['año_semana'] = resumen_pivot['año'].astype(str) + '-W' + \
                                  resumen_pivot['semana'].astype(str).str.zfill(2)
    
    return resumen_pivot.round(2)


def calcular_estado_semanal(df, gasto_diario_referencia):
    """
    Estado semanal: comparar el gasto acumulado en la semana actual con el valor de 
    "gasto diario de referencia × 7" y devolver si el usuario "supera" o está "dentro" 
    del presupuesto semanal.
    """
    if df.empty or gasto_diario_referencia == 0:
        return {
            'estado': 'Sin datos',
            'gasto_semana_actual': 0,
            'presupuesto_semanal': 0,
            'diferencia': 0
        }
    
    # Obtener la fecha actual (simular con la fecha más reciente del dataset)
    fecha_actual = df['fecha'].max()
    año_actual = fecha_actual.year
    semana_actual = fecha_actual.isocalendar().week
    
    # Filtrar gastos de la semana actual
    gastos_semana_actual = df[
        (df['año'] == año_actual) & 
        (df['semana'] == semana_actual) & 
        (df['tipo'] == 'Gasto')
    ]['monto'].sum()
    
    # Calcular presupuesto semanal
    presupuesto_semanal = gasto_diario_referencia * 7
    
    # Calcular diferencia
    diferencia = gastos_semana_actual - presupuesto_semanal
    
    # Determinar estado
    if diferencia > 0:
        estado = 'supera'
    else:
        estado = 'dentro'
    
    return {
        'estado': estado,
        'gasto_semana_actual': round(gastos_semana_actual, 2),
        'presupuesto_semanal': round(presupuesto_semanal, 2),
        'diferencia': round(diferencia, 2),
        'semana': f"{año_actual}-W{semana_actual:02d}"
    }


def calcular_saldo_diario_acumulado(df):
    """
    Calcula el saldo acumulado día a día para gráficos de evolución diaria.
    """
    if df.empty:
        return pd.DataFrame()
    
    # Agrupar por fecha y tipo
    resumen_diario = df.groupby(['fecha', 'tipo'])['monto'].sum().reset_index()
    
    # Pivotar para tener ingresos y gastos separados
    resumen_pivot = resumen_diario.pivot_table(
        index='fecha', 
        columns='tipo', 
        values='monto', 
        fill_value=0
    ).reset_index()
    
    # Asegurar columnas
    if 'Ingreso' not in resumen_pivot.columns:
        resumen_pivot['Ingreso'] = 0
    if 'Gasto' not in resumen_pivot.columns:
        resumen_pivot['Gasto'] = 0
    
    # Calcular neto diario
    resumen_pivot['neto_diario'] = resumen_pivot['Ingreso'] - resumen_pivot['Gasto']
    
    # Ordenar por fecha
    resumen_pivot = resumen_pivot.sort_values('fecha')
    
    # Calcular saldo acumulado
    resumen_pivot['saldo_acumulado'] = resumen_pivot['neto_diario'].cumsum()
    
    # Formatear fecha para gráficos
    resumen_pivot['fecha_str'] = resumen_pivot['fecha'].dt.strftime('%Y-%m-%d')
    
    return resumen_pivot.round(2)


def calcular_todas_agregaciones(df):
    """
    Función principal que calcula todas las agregaciones necesarias.
    Retorna un diccionario con todos los cálculos.
    """
    # Resumen mensual
    resumen_mensual = calcular_resumen_mensual(df)
    
    # Promedios mensuales
    promedios = calcular_promedio_mensual(resumen_mensual)
    
    # Gasto diario de referencia
    gasto_diario_referencia = calcular_gasto_diario_referencia(promedios['gasto_promedio'])
    
    # Resumen semanal
    resumen_semanal = calcular_resumen_semanal(df)
    
    # Estado semanal
    estado_semanal = calcular_estado_semanal(df, gasto_diario_referencia)
    
    # Saldo diario acumulado
    saldo_diario = calcular_saldo_diario_acumulado(df)
    
    return {
        'resumen_mensual': resumen_mensual.to_dict('records'),
        'resumen_semanal': resumen_semanal.to_dict('records'),
        'saldo_diario': saldo_diario.to_dict('records'),
        'promedios': promedios,
        'gasto_diario_referencia': gasto_diario_referencia,
        'estado_semanal': estado_semanal
    }

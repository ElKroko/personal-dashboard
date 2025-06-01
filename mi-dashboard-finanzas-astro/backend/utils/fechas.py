import pandas as pd
from datetime import datetime


def agregar_columnas_tiempo(df):
    """
    Función que toma el DataFrame ya limpio y crea columnas adicionales:
    - año (año de la fecha)
    - mes (número de mes) 
    - dia (día del mes)
    - semana (semana ISO)
    Para facilitar luego los agrupamientos.
    """
    if 'fecha' not in df.columns:
        raise Exception("El DataFrame debe contener la columna 'fecha'")
    
    # Hacer una copia para no modificar el original
    df_with_time = df.copy()
    
    # Asegurar que la columna fecha sea datetime
    df_with_time['fecha'] = pd.to_datetime(df_with_time['fecha'])
    
    # Agregar columnas de tiempo
    df_with_time['año'] = df_with_time['fecha'].dt.year
    df_with_time['mes'] = df_with_time['fecha'].dt.month
    df_with_time['dia'] = df_with_time['fecha'].dt.day
    df_with_time['semana'] = df_with_time['fecha'].dt.isocalendar().week
    
    # Agregar algunas columnas adicionales útiles
    df_with_time['dia_semana'] = df_with_time['fecha'].dt.dayofweek  # 0=Lunes, 6=Domingo
    df_with_time['nombre_mes'] = df_with_time['fecha'].dt.month_name()
    df_with_time['año_mes'] = df_with_time['fecha'].dt.strftime('%Y-%m')
    df_with_time['año_semana'] = df_with_time['fecha'].dt.strftime('%Y-W%U')
    
    return df_with_time


def obtener_rango_fechas(df):
    """
    Función auxiliar para obtener el rango de fechas del DataFrame.
    Retorna fecha mínima y máxima.
    """
    if 'fecha' not in df.columns:
        raise Exception("El DataFrame debe contener la columna 'fecha'")
    
    fecha_min = df['fecha'].min()
    fecha_max = df['fecha'].max()
    
    return {
        'fecha_inicio': fecha_min.strftime('%Y-%m-%d'),
        'fecha_fin': fecha_max.strftime('%Y-%m-%d'),
        'dias_totales': (fecha_max - fecha_min).days + 1
    }


def filtrar_por_periodo(df, año=None, mes=None, semana=None):
    """
    Función para filtrar el DataFrame por período específico.
    """
    df_filtrado = df.copy()
    
    if año is not None:
        df_filtrado = df_filtrado[df_filtrado['año'] == año]
    
    if mes is not None:
        df_filtrado = df_filtrado[df_filtrado['mes'] == mes]
    
    if semana is not None:
        df_filtrado = df_filtrado[df_filtrado['semana'] == semana]
    
    return df_filtrado


def obtener_periodos_disponibles(df):
    """
    Función para obtener los períodos disponibles en el DataFrame.
    Retorna listas de años, meses y semanas disponibles.
    """
    if not all(col in df.columns for col in ['año', 'mes', 'semana']):
        raise Exception("El DataFrame debe contener las columnas de tiempo")
    
    años = sorted(df['año'].unique().tolist())
    meses = sorted(df['mes'].unique().tolist())
    semanas = sorted(df['semana'].unique().tolist())
    
    # También obtener combinaciones año-mes disponibles
    años_meses = sorted(df['año_mes'].unique().tolist())
    años_semanas = sorted(df['año_semana'].unique().tolist())
    
    return {
        'años': años,
        'meses': meses,
        'semanas': semanas,
        'años_meses': años_meses,
        'años_semanas': años_semanas
    }

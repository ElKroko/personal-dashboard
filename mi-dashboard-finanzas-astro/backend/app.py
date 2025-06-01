from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import pandas as pd
import os
import tempfile
import numpy as np
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Importar utilidades locales
from utils.leer_excel import procesar_archivo_excel
from utils.categorizar import aplicar_categorizacion
from utils.fechas import agregar_columnas_tiempo, obtener_rango_fechas, obtener_periodos_disponibles
from utils.agregaciones import calcular_todas_agregaciones
from utils.bd import DatabaseManager

# Modelos Pydantic para requests
class CategoriaUpdate(BaseModel):
    nueva_categoria: str

# Instancia global del manejador de base de datos (opcional)
db_manager = None

def limpiar_datos_para_json(obj):
    """
    Limpia un objeto de datos pandas para que sea compatible con JSON.
    Convierte NaN, inf, -inf y Timestamps a valores serializables.
    """
    if isinstance(obj, dict):
        return {k: limpiar_datos_para_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [limpiar_datos_para_json(item) for item in obj]
    elif isinstance(obj, (pd.Series, pd.DataFrame)):
        # Convertir a dict y luego limpiar recursivamente
        return limpiar_datos_para_json(obj.to_dict())
    elif isinstance(obj, pd.Timestamp):
        # Convertir Timestamp a string ISO format
        if pd.isna(obj):
            return None
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, (float, np.floating)):
        if pd.isna(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, (int, np.integer)):
        if pd.isna(obj):
            return None
        return int(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, str):
        return str(obj)
    elif pd.isna(obj):
        return None
    else:
        # Para cualquier otro tipo, intentar convertir a tipo básico
        try:
            if hasattr(obj, 'item'):  # numpy scalars
                return obj.item()
            return obj
        except:
            return str(obj)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejar el ciclo de vida de la aplicación"""
    global db_manager
    # Startup
    try:
        db_manager = DatabaseManager()
        print("Base de datos inicializada correctamente")
    except Exception as e:
        print(f"Warning: No se pudo inicializar la base de datos: {e}")
        db_manager = None
    
    yield
    
    # Shutdown
    if db_manager:
        db_manager.cerrar_conexion()

app = FastAPI(
    title="Dashboard Finanzas API", 
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS para permitir llamadas desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:4321",  # Astro dev server default
        "http://localhost:4322",  # Astro dev server (your current port)
        "http://localhost:4323",  # Astro dev server alternate
        "http://127.0.0.1:4322",  # Alternative localhost format
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raíz para verificar que la API está funcionando"""
    return {"message": "Dashboard Finanzas API está funcionando"}

@app.post("/procesar/")
async def procesar_archivo(
    archivo: UploadFile = File(...),
    guardar_bd: Optional[bool] = Form(False),
    modo_bd: Optional[str] = Form("append")
):
    """
    Endpoint principal que:
    1. Acepta un archivo .xlsx en form-data
    2. Valida extensión y guarda temporalmente el archivo
    3. Invoca las funciones de lectura, limpieza, categorización y agregación
    4. Genera un objeto JSON con todas las métricas calculadas
    5. Opcionalmente guarda en base de datos
    6. Elimina el archivo temporal y devuelve la respuesta JSON
    """
    
    # Validar extensión del archivo
    if not archivo.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400, 
            detail="El archivo debe ser un Excel (.xlsx o .xls)"
        )
    
    # Crear archivo temporal
    temp_file = None
    
    try:
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            content = await archivo.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # 1. Leer y limpiar Excel
        df = procesar_archivo_excel(temp_file_path)
        
        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="El archivo Excel está vacío o no contiene datos válidos"
            )
        
        # 2. Aplicar categorización
        df = aplicar_categorizacion(df)
        
        # 3. Agregar columnas de tiempo
        df = agregar_columnas_tiempo(df)
        
        # 4. Calcular todas las agregaciones
        agregaciones = calcular_todas_agregaciones(df)
        
        # 5. Obtener información adicional
        rango_fechas = obtener_rango_fechas(df)
        periodos_disponibles = obtener_periodos_disponibles(df)
          # 6. Preparar lista de transacciones para el frontend
        transacciones_list = df.to_dict('records')
        
        # Convertir fechas a strings para JSON
        for transaccion in transacciones_list:
            if pd.notna(transaccion['fecha']):
                if hasattr(transaccion['fecha'], 'strftime'):
                    transaccion['fecha'] = transaccion['fecha'].strftime('%Y-%m-%d')
                elif isinstance(transaccion['fecha'], str):
                    # Ya es string, mantener como está
                    pass
        
        # 7. Guardar en base de datos si se solicita
        if guardar_bd and db_manager:
            try:
                db_manager.guardar_dataframe(df, modo=modo_bd)
                bd_status = "Datos guardados en base de datos"
            except Exception as e:
                bd_status = f"Error al guardar en BD: {str(e)}"
        else:
            bd_status = "No se guardó en base de datos"
          # 8. Preparar respuesta JSON
        response_data = {
            "status": "success",
            "message": "Archivo procesado correctamente",
            "bd_status": bd_status,
            "rango_fechas": rango_fechas,
            "periodos_disponibles": periodos_disponibles,
            "total_transacciones": len(transacciones_list),
            "transacciones": transacciones_list,
            "resumen_mensual": agregaciones['resumen_mensual'],
            "resumen_semanal": agregaciones['resumen_semanal'],
            "saldo_diario": agregaciones['saldo_diario'],
            "promedios": agregaciones['promedios'],
            "gasto_diario_referencia": agregaciones['gasto_diario_referencia'],
            "estado_semanal": agregaciones['estado_semanal']
        }
        
        # Limpiar datos para JSON antes de enviar la respuesta
        response_data = limpiar_datos_para_json(response_data)
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar archivo: {str(e)}"
        )
    
    finally:
        # Limpiar archivo temporal
        if temp_file and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.get("/historial/")
async def obtener_historial():
    """
    Endpoint para obtener todas las transacciones guardadas en la base de datos.
    Útil cuando no se quiere volver a subir archivos.
    """
    if not db_manager:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no disponible"
        )
    
    try:
        # Obtener todas las transacciones
        df = db_manager.obtener_todas_transacciones()
        
        if df.empty:
            return JSONResponse(content={
                "status": "success",
                "message": "No hay transacciones en la base de datos",
                "total_transacciones": 0,
                "transacciones": [],
                "resumen_mensual": [],
                "resumen_semanal": [],
                "saldo_diario": [],
                "promedios": {"ingreso_promedio": 0, "gasto_promedio": 0},
                "gasto_diario_referencia": 0,
                "estado_semanal": {"estado": "Sin datos"}
            })
        
        # Asegurar que las columnas de tiempo estén presentes
        df = agregar_columnas_tiempo(df)
        
        # Calcular agregaciones
        agregaciones = calcular_todas_agregaciones(df)
        
        # Obtener información adicional
        rango_fechas = obtener_rango_fechas(df)
        periodos_disponibles = obtener_periodos_disponibles(df)
          # Preparar lista de transacciones
        transacciones_list = df.to_dict('records')
        
        # Convertir fechas a strings
        for transaccion in transacciones_list:
            if pd.notna(transaccion['fecha']):
                if hasattr(transaccion['fecha'], 'strftime'):
                    transaccion['fecha'] = transaccion['fecha'].strftime('%Y-%m-%d')
                elif isinstance(transaccion['fecha'], str):
                    # Ya es string, mantener como está
                    pass
        
        response_data = {
            "status": "success",
            "message": "Historial obtenido correctamente",
            "rango_fechas": rango_fechas,
            "periodos_disponibles": periodos_disponibles,
            "total_transacciones": len(transacciones_list),
            "transacciones": transacciones_list,
            "resumen_mensual": agregaciones['resumen_mensual'],
            "resumen_semanal": agregaciones['resumen_semanal'],
            "saldo_diario": agregaciones['saldo_diario'],
            "promedios": agregaciones['promedios'],
            "gasto_diario_referencia": agregaciones['gasto_diario_referencia'],
            "estado_semanal": agregaciones['estado_semanal']
        }
        
        # Limpiar datos para JSON antes de enviar la respuesta
        response_data = limpiar_datos_para_json(response_data)
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener historial: {str(e)}"
        )

@app.delete("/historial/")
async def limpiar_historial():
    """
    Endpoint para limpiar todas las transacciones de la base de datos.
    """
    if not db_manager:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no disponible"
        )
    
    try:
        db_manager.limpiar_base_datos()
        return JSONResponse(content={
            "status": "success",
            "message": "Historial limpiado correctamente"
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al limpiar historial: {str(e)}"
        )

@app.get("/stats/")
async def obtener_estadisticas():
    """
    Endpoint para obtener estadísticas básicas de la base de datos.
    """
    if not db_manager:
        return JSONResponse(content={
            "bd_disponible": False,
            "total_transacciones": 0
        })
    
    try:
        total_transacciones = db_manager.contar_transacciones()
        
        return JSONResponse(content={
            "bd_disponible": True,
            "total_transacciones": total_transacciones
        })
        
    except Exception as e:
        return JSONResponse(content={
            "bd_disponible": False,
            "total_transacciones": 0,
            "error": str(e)
        })

@app.post("/cargar-tef-locales/")
async def cargar_archivos_tef_locales():
    """
    Endpoint para cargar automáticamente todos los archivos TEF 
    que están en la carpeta data/load_excels/
    """
    load_excels_path = os.path.join(os.path.dirname(__file__), "data", "load_excels")
    
    if not os.path.exists(load_excels_path):
        raise HTTPException(
            status_code=404,
            detail="Carpeta load_excels no encontrada"
        )
    
    # Buscar archivos Excel en la carpeta
    archivos_excel = []
    for archivo in os.listdir(load_excels_path):
        if archivo.endswith(('.xlsx', '.xls')):
            archivos_excel.append(os.path.join(load_excels_path, archivo))
    
    if not archivos_excel:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron archivos Excel en load_excels"
        )
    
    try:
        # Lista para almacenar todos los DataFrames
        dataframes = []
        archivos_procesados = []
        
        # Procesar cada archivo
        for archivo_path in archivos_excel:
            try:
                df = procesar_archivo_excel(archivo_path)
                if not df.empty:
                    dataframes.append(df)
                    archivos_procesados.append(os.path.basename(archivo_path))
            except Exception as e:
                print(f"Error procesando {archivo_path}: {e}")
                continue
        
        if not dataframes:
            raise HTTPException(
                status_code=400,
                detail="No se pudieron procesar los archivos TEF"
            )
        
        # Combinar todos los DataFrames
        df_completo = pd.concat(dataframes, ignore_index=True)
        
        # Eliminar duplicados si los hay (basado en columnas clave)
        columnas_clave = ['fecha', 'monto', 'detalle']
        df_completo = df_completo.drop_duplicates(subset=columnas_clave, keep='first')
        
        # 2. Aplicar categorización
        df_completo = aplicar_categorizacion(df_completo)
        
        # 3. Agregar columnas de tiempo
        df_completo = agregar_columnas_tiempo(df_completo)
        
        # 4. Calcular todas las agregaciones
        agregaciones = calcular_todas_agregaciones(df_completo)
        
        # 5. Obtener información adicional
        rango_fechas = obtener_rango_fechas(df_completo)
        periodos_disponibles = obtener_periodos_disponibles(df_completo)
          # 6. Preparar lista de transacciones para el frontend
        transacciones_list = df_completo.to_dict('records')
        
        # Convertir fechas a strings para JSON
        for transaccion in transacciones_list:
            if pd.notna(transaccion['fecha']):
                if hasattr(transaccion['fecha'], 'strftime'):
                    transaccion['fecha'] = transaccion['fecha'].strftime('%Y-%m-%d')
                elif isinstance(transaccion['fecha'], str):
                    # Ya es string, mantener como está
                    pass
        
        # 7. Guardar en base de datos si está disponible
        bd_status = "Base de datos no disponible"
        if db_manager:
            try:
                # Limpiar la base de datos antes de cargar los nuevos datos
                db_manager.limpiar_base_datos()
                db_manager.guardar_dataframe(df_completo, modo="replace")
                bd_status = "Datos guardados en base de datos"
            except Exception as e:
                bd_status = f"Error al guardar en BD: {str(e)}"
          # 8. Preparar respuesta JSON
        response_data = {
            "status": "success",
            "message": f"Se procesaron {len(archivos_procesados)} archivos TEF correctamente",
            "archivos_procesados": archivos_procesados,
            "bd_status": bd_status,
            "rango_fechas": rango_fechas,
            "periodos_disponibles": periodos_disponibles,
            "total_transacciones": len(transacciones_list),
            "transacciones": transacciones_list,
            "resumen_mensual": agregaciones['resumen_mensual'],
            "resumen_semanal": agregaciones['resumen_semanal'],
            "saldo_diario": agregaciones['saldo_diario'],
            "promedios": agregaciones['promedios'],
            "gasto_diario_referencia": agregaciones['gasto_diario_referencia'],
            "estado_semanal": agregaciones['estado_semanal']
        }
        
        # Limpiar datos para JSON antes de enviar la respuesta
        response_data = limpiar_datos_para_json(response_data)
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar archivos TEF: {str(e)}"
        )

# =====================================================
# NUEVOS ENDPOINTS PARA SISTEMA INTERACTIVO
# =====================================================

@app.get("/transacciones/")
async def obtener_transacciones(
    fecha_desde: Optional[str] = Query(None, description="Fecha desde en formato YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta en formato YYYY-MM-DD"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    tipo_movimiento: Optional[str] = Query(None, description="Filtrar por tipo (Ingreso/Gasto)"),
    texto_busqueda: Optional[str] = Query(None, description="Buscar en detalle de transacciones"),
    solo_sin_categorizar: Optional[bool] = Query(False, description="Solo mostrar transacciones sin categorizar"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=500, description="Tamaño de página")
):
    """
    Obtiene transacciones con filtros opcionales y paginación.
    """
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Base de datos no disponible")
        
        # Obtener todas las transacciones
        df = db_manager.obtener_todas_transacciones()
        
        if df.empty:
            return JSONResponse(content={
                "transacciones": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            })
        
        # Aplicar filtros
        if fecha_desde:
            df = df[df['fecha'] >= fecha_desde]
        
        if fecha_hasta:
            df = df[df['fecha'] <= fecha_hasta]
        
        if categoria:
            df = df[df['categoria'] == categoria]
        
        if tipo_movimiento:
            df = df[df['tipo'] == tipo_movimiento]
        
        if texto_busqueda:
            df = df[df['detalle'].str.contains(texto_busqueda, case=False, na=False)]
        
        if solo_sin_categorizar:
            df = df[df['categoria'] == "Sin categorizar"]
        
        # Ordenar por fecha descendente
        df = df.sort_values('fecha', ascending=False)
        
        # Calcular paginación
        total = len(df)
        offset = (page - 1) * page_size
        df_paginated = df.iloc[offset:offset + page_size]
          # Convertir a lista de diccionarios
        transacciones = []
        for _, row in df_paginated.iterrows():
            transacciones.append({
                'id': int(row['id']) if 'id' in row and pd.notna(row['id']) else None,
                'fecha': row['fecha'].strftime('%Y-%m-%d') if pd.notna(row['fecha']) and hasattr(row['fecha'], 'strftime') else str(row['fecha']) if pd.notna(row['fecha']) else None,
                'detalle': str(row['detalle']) if pd.notna(row['detalle']) else '',
                'monto': float(row['monto']) if pd.notna(row['monto']) else 0.0,
                'tipo': str(row['tipo']) if pd.notna(row['tipo']) else '',
                'categoria': str(row['categoria']) if pd.notna(row['categoria']) else 'Sin categorizar',
                'tipo_regla': str(row['tipo_regla']) if 'tipo_regla' in row and pd.notna(row['tipo_regla']) else 'mapeo_por_palabra_clave',
                'fecha_modificacion': row['fecha_modificacion'].strftime('%Y-%m-%d %H:%M:%S') if 'fecha_modificacion' in row and pd.notna(row['fecha_modificacion']) else None
            })
        
        total_pages = (total + page_size - 1) // page_size
        
        return JSONResponse(content={
            "transacciones": transacciones,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener transacciones: {str(e)}")

@app.get("/resumen/categorias/")
async def obtener_resumen_categorias(
    fecha_desde: Optional[str] = Query(None, description="Fecha desde en formato YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta en formato YYYY-MM-DD")
):
    """
    Obtiene resumen por categorías con filtros de fecha opcionales.
    """
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Base de datos no disponible")
        
        # Obtener todas las transacciones
        df = db_manager.obtener_todas_transacciones()
        
        if df.empty:
            return JSONResponse(content={"categorias": []})
        
        # Aplicar filtros de fecha
        if fecha_desde:
            df = df[df['fecha'] >= fecha_desde]
        
        if fecha_hasta:
            df = df[df['fecha'] <= fecha_hasta]
        
        # Agrupar por categoría y tipo
        resumen = df.groupby(['categoria', 'tipo'])['monto'].sum().reset_index()
        
        # Crear estructura de datos para el resumen
        categorias_dict = {}
        for _, row in resumen.iterrows():
            categoria = row['categoria']
            tipo = row['tipo']
            monto = float(row['monto'])
            
            if categoria not in categorias_dict:
                categorias_dict[categoria] = {
                    'categoria': categoria,
                    'total_ingresos': 0.0,
                    'total_gastos': 0.0,
                    'total_neto': 0.0
                }
            
            if tipo == 'Ingreso':
                categorias_dict[categoria]['total_ingresos'] = monto
            else:
                categorias_dict[categoria]['total_gastos'] = monto
        
        # Calcular neto y convertir a lista
        categorias_lista = []
        for categoria_data in categorias_dict.values():
            categoria_data['total_neto'] = categoria_data['total_ingresos'] + categoria_data['total_gastos']
            categorias_lista.append(categoria_data)
        
        # Ordenar por total neto (valor absoluto) descendente
        categorias_lista.sort(key=lambda x: abs(x['total_neto']), reverse=True)
        
        return JSONResponse(content={"categorias": categorias_lista})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener resumen por categorías: {str(e)}")

@app.patch("/transacciones/{transaccion_id}/categoria")
async def actualizar_categoria_transaccion(transaccion_id: int, categoria_update: CategoriaUpdate):
    """
    Actualiza la categoría de una transacción específica.
    """
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Base de datos no disponible")
        
        # Actualizar la categoría en la base de datos
        resultado = db_manager.actualizar_categoria_transaccion(
            transaccion_id=transaccion_id,
            nueva_categoria=categoria_update.nueva_categoria
        )
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        
        # Obtener la transacción actualizada
        df = db_manager.obtener_transaccion_por_id(transaccion_id)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="Transacción no encontrada después de actualizar")
        row = df.iloc[0]
        transaccion_actualizada = {
            'id': int(row['id']),
            'fecha': row['fecha'].strftime('%Y-%m-%d') if pd.notna(row['fecha']) and hasattr(row['fecha'], 'strftime') else str(row['fecha']) if pd.notna(row['fecha']) else None,
            'detalle': str(row['detalle']),
            'monto': float(row['monto']),
            'tipo': str(row['tipo']),
            'categoria': str(row['categoria']),
            'tipo_regla': str(row['tipo_regla']),
            'fecha_modificacion': row['fecha_modificacion'].strftime('%Y-%m-%d %H:%M:%S') if 'fecha_modificacion' in row and pd.notna(row['fecha_modificacion']) and hasattr(row['fecha_modificacion'], 'strftime') else str(row['fecha_modificacion']) if 'fecha_modificacion' in row and pd.notna(row['fecha_modificacion']) else None
        }
        
        return JSONResponse(content={
            "status": "success",
            "message": "Categoría actualizada exitosamente",
            "transaccion": transaccion_actualizada
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar categoría: {str(e)}")

@app.get("/categorias/reglas/")
async def obtener_reglas_categorizacion():
    """
    Obtiene las reglas de categorización actuales (diccionario de palabras clave).
    """
    try:
        from utils.categorizar import CATEGORIA_KEYWORDS
        
        # Convertir el diccionario a una estructura más amigable para el frontend
        reglas = []
        for categoria, palabras in CATEGORIA_KEYWORDS.items():
            reglas.append({
                'categoria': categoria,
                'palabras_clave': palabras,
                'total_palabras': len(palabras)
            })
        
        # Ordenar por categoría
        reglas.sort(key=lambda x: x['categoria'])
        
        return JSONResponse(content={
            "reglas": reglas,
            "total_categorias": len(reglas)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reglas de categorización: {str(e)}")

@app.get("/transacciones/sin-categorizar/")
async def obtener_transacciones_sin_categorizar():
    """
    Obtiene todas las transacciones sin categorizar con sugerencias.
    """
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Base de datos no disponible")
        
        # Obtener transacciones sin categorizar
        df = db_manager.obtener_todas_transacciones()
        df_sin_cat = df[df['categoria'] == "Sin categorizar"]
        
        if df_sin_cat.empty:
            return JSONResponse(content={
                "transacciones": [],
                "total": 0,
                "mensaje": "No hay transacciones sin categorizar"
            })
        
        # Importar función de sugerencias
        from utils.categorizar import sugerir_categoria
        
        transacciones = []
        for _, row in df_sin_cat.iterrows():
            # Generar sugerencia para cada transacción
            sugerencia = sugerir_categoria(row['detalle'])
            transacciones.append({
                'id': int(row['id']) if 'id' in row and pd.notna(row['id']) else None,
                'fecha': row['fecha'].strftime('%Y-%m-%d') if pd.notna(row['fecha']) and hasattr(row['fecha'], 'strftime') else str(row['fecha']) if pd.notna(row['fecha']) else None,
                'detalle': str(row['detalle']) if pd.notna(row['detalle']) else '',
                'monto': float(row['monto']) if pd.notna(row['monto']) else 0.0,
                'tipo': str(row['tipo']) if pd.notna(row['tipo']) else '',
                'categoria': str(row['categoria']) if pd.notna(row['categoria']) else 'Sin categorizar',
                'sugerencia': sugerencia,
                'tipo_regla': str(row['tipo_regla']) if 'tipo_regla' in row and pd.notna(row['tipo_regla']) else 'sin_coincidencias'
            })
        
        return JSONResponse(content={
            "transacciones": transacciones,
            "total": len(transacciones)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener transacciones sin categorizar: {str(e)}")

# =================== ENDPOINTS PARA CATEGORÍAS PERSONALIZADAS ===================

@app.get("/categorias-custom/")
async def obtener_categorias_custom():
    """
    Obtiene todas las categorías personalizadas.
    """
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Base de datos no disponible")
        
        categorias = db_manager.obtener_categorias_custom()
        
        return JSONResponse(content={
            "status": "success",
            "categorias": categorias,
            "total": len(categorias)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener categorías personalizadas: {str(e)}")

@app.post("/categorias-custom/")
async def crear_categoria_custom(categoria_data: dict):
    """
    Crea una nueva categoría personalizada.
    
    Body JSON: {
        "nombre_categoria": "Gasto - Mascotas",
        "palabras_clave": ["veterinario", "comida perro", "petshop"],
        "descripcion": "Gastos relacionados con mascotas"
    }
    """
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Base de datos no disponible")
        
        # Validar campos requeridos
        if "nombre_categoria" not in categoria_data:
            raise HTTPException(status_code=400, detail="Campo 'nombre_categoria' requerido")
        
        if "palabras_clave" not in categoria_data:
            raise HTTPException(status_code=400, detail="Campo 'palabras_clave' requerido")
        
        # Validar que palabras_clave sea una lista
        if not isinstance(categoria_data["palabras_clave"], list):
            raise HTTPException(status_code=400, detail="Campo 'palabras_clave' debe ser una lista")
        
        nombre_categoria = categoria_data["nombre_categoria"]
        palabras_clave = categoria_data["palabras_clave"]
        descripcion = categoria_data.get("descripcion", "")
        
        # Crear la categoría
        nueva_categoria = db_manager.crear_categoria_custom(
            nombre_categoria=nombre_categoria,
            palabras_clave=palabras_clave,
            descripcion=descripcion
        )
        
        return JSONResponse(content={
            "status": "success",
            "message": "Categoría creada correctamente",
            "categoria": nueva_categoria
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear categoría: {str(e)}")

@app.put("/categorias-custom/{categoria_id}")
async def actualizar_categoria_custom(categoria_id: int, categoria_data: dict):
    """
    Actualiza una categoría personalizada existente.
    
    Body JSON: {
        "nombre_categoria": "Nuevo nombre",
        "palabras_clave": ["nueva", "lista", "palabras"],
        "descripcion": "Nueva descripción"
    }
    """
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Base de datos no disponible")
        
        # Extraer campos a actualizar
        nombre_categoria = categoria_data.get("nombre_categoria")
        palabras_clave = categoria_data.get("palabras_clave")
        descripcion = categoria_data.get("descripcion")
        
        # Validar que palabras_clave sea una lista si se proporciona
        if palabras_clave is not None and not isinstance(palabras_clave, list):
            raise HTTPException(status_code=400, detail="Campo 'palabras_clave' debe ser una lista")
        
        # Actualizar la categoría
        categoria_actualizada = db_manager.actualizar_categoria_custom(
            categoria_id=categoria_id,
            nombre_categoria=nombre_categoria,
            palabras_clave=palabras_clave,
            descripcion=descripcion
        )
        
        return JSONResponse(content={
            "status": "success",
            "message": "Categoría actualizada correctamente",
            "categoria": categoria_actualizada
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar categoría: {str(e)}")

@app.delete("/categorias-custom/{categoria_id}")
async def eliminar_categoria_custom(categoria_id: int):
    """
    Elimina (desactiva) una categoría personalizada.
    """
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Base de datos no disponible")
        
        # Eliminar la categoría
        resultado = db_manager.eliminar_categoria_custom(categoria_id)
        
        return JSONResponse(content={
            "status": "success",
            "message": "Categoría eliminada correctamente"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar categoría: {str(e)}")

@app.get("/categorias-todas/")
async def obtener_todas_las_categorias():
    """
    Obtiene todas las categorías disponibles (predefinidas + personalizadas).
    """
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Base de datos no disponible")
        
        todas_categorias_dict = db_manager.obtener_todas_categorias_con_custom()
        
        # Convertir a lista de nombres de categorías para el frontend
        categorias_lista = list(todas_categorias_dict.keys())
        
        return JSONResponse(content={
            "status": "success",
            "categorias": categorias_lista,
            "categorias_detalladas": todas_categorias_dict,
            "total": len(categorias_lista)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener todas las categorías: {str(e)}")

@app.post("/recategorizar-transacciones/")
async def recategorizar_transacciones():
    """
    Recategoriza todas las transacciones usando las reglas actuales (incluyendo categorías personalizadas).
    """
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Base de datos no disponible")
        
        from utils.categorizar import aplicar_categorizacion
        
        # Obtener todas las transacciones
        df = db_manager.obtener_todas_transacciones()
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No hay transacciones para recategorizar")
        
        # Aplicar nueva categorización
        df_recategorizado = aplicar_categorizacion(df)
        
        # Actualizar cada transacción en la base de datos
        transacciones_actualizadas = 0
        for _, row in df_recategorizado.iterrows():
            if 'id' in row and pd.notna(row['id']):
                resultado = db_manager.actualizar_categoria_transaccion(
                    transaccion_id=int(row['id']),
                    nueva_categoria=row['categoria']
                )
                if resultado:
                    transacciones_actualizadas += 1
        
        return JSONResponse(content={
            "status": "success",
            "message": f"Se recategorizaron {transacciones_actualizadas} transacciones",
            "transacciones_actualizadas": transacciones_actualizadas,
            "total_transacciones": len(df)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al recategorizar transacciones: {str(e)}")

# Modelos Pydantic para requests
class CategoriaUpdate(BaseModel):
    nueva_categoria: str

class TransaccionResponse(BaseModel):
    id: int
    fecha: str
    detalle: str
    monto: float
    tipo: str
    categoria: str
    tipo_regla: str
    fecha_modificacion: str

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

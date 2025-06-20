import pandas as pd
import re


def definir_categorias():
    """
    Define un diccionario de palabras clave que permiten mapear el contenido 
    del campo "detalle" a una categoría específica.
    Optimizado para datos de transferencias bancarias chilenas.
    """
    categorias = {
        # Ingresos
        'Ingreso - Sueldos': [
            'SUELDO', 'SALARIO', 'NOMINA', 'PAGO EMPLEADO', 'HONORARIOS',
            'REMUNERACION', 'TRABAJO', 'EMPRESA', 'EMPLEADOR', 'LIQUIDACION',
            'GRATIFICACION', 'AGUINALDO', 'BONO VACACIONES'
        ],
        'Ingreso - Transferencias': [
            'TRANSFERENCIA RECIBIDA', 'DEPOSITO', 'ABONO', 'INGRESO',
            'PAGO RECIBIDO', 'COBRO', 'GIRO RECIBIDO', 'ENVIO RECIBIDO'
        ],
        'Ingreso - Otros': [
            'REINTEGRO', 'DEVOLUCION', 'INTERESES A FAVOR', 'DIVIDENDOS',
            'BONO', 'PREMIO', 'SUBSIDIO', 'PENSION', 'JUBILACION', 'AFP',
            'ISAPRE DEVOLUCION', 'REEMBOLSO'
        ],
        
        # Gastos - Básicos
        'Gasto - Alimentos': [
            'SUPERMERCADO', 'MERCADO', 'ALMACEN', 'PANADERIA', 'CARNICERIA',
            'VERDULERIA', 'COMIDA', 'RESTAURANT', 'DELIVERY', 'RAPPI', 'UBER EATS',
            'JUMBO', 'LIDER', 'SANTA ISABEL', 'TOTTUS', 'UNIMARC', 'ACUENTA',
            'MALL', 'FERIA', 'DESPENSA', 'MINIMARKET', 'BOTILLERIA', 'MARISQUERIA',
            'PIZZERIA', 'CAFETERIA', 'PASTELERIA', 'HELADERIA', 'FERIA LIBRE',
            'ABARROTES', 'PROVEEDORA'
        ],
        'Gasto - Transporte': [
            'COMBUSTIBLE', 'GASOLINA', 'NAFTA', 'TAXI', 'UBER', 'COLECTIVO',
            'SUBTE', 'TREN', 'PEAJE', 'ESTACIONAMIENTO', 'PARKING', 'METRO',
            'TRANSANTIAGO', 'BIP', 'COPEC', 'SHELL', 'PETROBRAS', 'ESSO',
            'AUTOBUS', 'MICRO', 'CABIFY', 'DIDI', 'REVISION TECNICA', 'PERMISO CIRCULACION',
            'SEGURO VEHICULO', 'MANTENSION AUTO', 'REPUESTOS', 'MECANICO'
        ],
        'Gasto - Servicios': [
            'LUZ', 'AGUA', 'GAS', 'TELEFONO', 'INTERNET', 'CABLE', 'ELECTRICIDAD',
            'CGE', 'CHILQUINTA', 'ENEL', 'AGUAS ANDINAS', 'ESSAL', 'METROGAS',
            'LIPIGAS', 'ENTEL', 'MOVISTAR', 'CLARO', 'WOM', 'VTR', 'GTD',
            'DIRECTV', 'CNT', 'TELEFONICA', 'MUNDO PACIFICO', 'ESSBIO'
        ],
        'Gasto - Vivienda': [
            'ARRIENDO', 'ALQUILER', 'RENTA', 'HIPOTECA', 'DIVIDENDO',
            'CONDOMINIO', 'ADMINISTRACION', 'COMUNIDAD', 'GASTOS COMUNES',
            'MANTENSION CASA', 'REPARACIONES', 'PINTURA', 'FERRETERIA',
            'CONSTRUCCION', 'MATERIALES'
        ],
        'Gasto - Salud': [
            'FARMACIA', 'MEDICO', 'HOSPITAL', 'CLINICA', 'CONSULTA',
            'CRUZ VERDE', 'SALCOBRAND', 'AHUMADA', 'FONASA', 'ISAPRE',
            'DENTAL', 'LABORATORIO', 'EXAMEN', 'MEDICAMENTOS', 'DOCTOR',
            'OFTALMOLOGIA', 'CARDIOLOGIA', 'PEDIATRA', 'PSICOLOGO',
            'KINESIOLOGIA', 'RAYOS X', 'ECOGRAFIA'
        ],
        'Gasto - Educación': [
            'COLEGIO', 'UNIVERSIDAD', 'INSTITUTO', 'CURSO', 'MATRICULA',
            'MENSUALIDAD', 'LIBROS', 'MATERIALES', 'ESCUELA', 'JARDIN',
            'EDUCACION', 'CAPACITACION', 'SEMINARIO', 'TALLER'
        ],
        'Gasto - Entretenimiento': [
            'CINE', 'TEATRO', 'CONCIERTO', 'BAR', 'PUB', 'DISCOTECA',
            'NETFLIX', 'SPOTIFY', 'STEAM', 'JUEGOS', 'GIMNASIO',
            'PISCINA', 'CLUB', 'DEPORTES', 'CANCHA', 'SUSCRIPCION',
            'ENTRADAS', 'ESPECTACULO'
        ],        'Gasto - Compras': [
            'ROPA', 'FALABELLA', 'RIPLEY', 'PARIS', 'HITES', 'AMAZON',
            'MERCADOLIBRE', 'ZARA', 'H&M', 'ADIDAS', 'NIKE', 'ZAPATERIA',
            'ELECTRODOMESTICOS', 'MUEBLES', 'DECORACION', 'PERFUMERIA',
            'JOYERIA', 'RELOJERIA', 'LIBRERIA', 'JUGUETERIA', 'COMPRAVENTA',
            'ANGELOCOMPRAVENTAS', 'TIENDA', 'COMERCIAL', 'VENTAS'
        ],'Gasto - Financiero': [
            'BANCO', 'COMISION', 'INTERES', 'CUOTA', 'CREDITO', 'PRESTAMO',
            'TARJETA', 'MANTENSION', 'ANUALIDAD', 'SEGURO', 'AFP',
            'BANCO CHILE', 'BANCO ESTADO', 'BCI', 'SANTANDER', 'ITAU',
            'SCOTIABANK', 'CORPBANCA', 'HSBC', 'FINTUAL', 'ADMINISTRADORA',
            'FONDOS', 'INVERSION', 'MUTUAL', 'RENTA FIJA', 'RENTA VARIABLE'
        ],        'Transferencias': [
            'TRANSFERENCIA', 'ENVIO', 'GIRO', 'PAGO A TERCEROS', 'ENVIO DINERO',
            'PAGO PERSONA', 'TERCERO', 'HERNIA', 'MAXIMILIANO', 'GALLARDO',
            'PEREZ', 'GONZALEZ', 'RODRIGUEZ', 'LOPEZ', 'MARTINEZ', 'GARCIA',
            'FERNANDEZ', 'SANCHEZ', 'MORALES', 'SILVA', 'CASTRO', 'ROJAS'
        ],
        'Retiros': [
            'CAJERO', 'ATM', 'RETIRO', 'EFECTIVO', 'RETIRO CAJERO',
            'CAJERO AUTOMATICO'
        ],
        'Impuestos y Gobierno': [
            'SII', 'IMPUESTO', 'CONTRIBUCIONES', 'PATENTE', 'TESORERIA',
            'MUNICIPALIDAD', 'REGISTRO CIVIL', 'NOTARIA', 'CONSERVADOR'
        ]
    }
    
    return categorias


def obtener_categorias_custom_desde_bd():
    """
    Obtiene las categorías personalizadas desde la base de datos.
    """
    try:
        from utils.bd import DatabaseManager
        db_manager = DatabaseManager()
        categorias_custom = db_manager.obtener_categorias_custom()
        db_manager.cerrar_conexion()
        
        # Convertir a formato compatible
        categorias_dict = {}
        for categoria in categorias_custom:
            categorias_dict[categoria['nombre_categoria']] = categoria['palabras_clave']
        
        return categorias_dict
    except Exception as e:
        print(f"Warning: No se pudieron cargar categorías personalizadas: {e}")
        return {}


def obtener_todas_las_categorias():
    """
    Combina categorías predefinidas con categorías personalizadas.
    """
    categorias_predefinidas = definir_categorias()
    categorias_custom = obtener_categorias_custom_desde_bd()
    
    # Combinar ambos diccionarios (las custom tienen prioridad)
    todas_categorias = {**categorias_predefinidas, **categorias_custom}
    return todas_categorias


def categorizar_transaccion(detalle, nombre_destino="", comentario="", monto=0):
    """
    Categoriza una transacción basándose en múltiples campos.
    Específicamente adaptado para datos de transferencias bancarias.
    """
    detalle_upper = str(detalle).upper()
    nombre_destino_upper = str(nombre_destino).upper()
    comentario_upper = str(comentario).upper()
    
    # Detectar transferencias personales por patrones de nombres
    def es_nombre_persona(texto):
        """Detecta si el texto parece ser un nombre de persona"""
        texto = texto.strip()
        if not texto or texto.isdigit():
            return False
        
        # Patrones comunes de nombres chilenos
        nombres_comunes = ['HERNIA', 'MAXIMILIANO', 'JUAN', 'MARIA', 'CARLOS', 'ANA', 
                          'LUIS', 'CARMEN', 'JOSE', 'PATRICIA', 'FRANCISCO', 'ROSA']
        apellidos_comunes = ['PEREZ', 'GONZALEZ', 'RODRIGUEZ', 'LOPEZ', 'MARTINEZ', 
                           'GARCIA', 'FERNANDEZ', 'SANCHEZ', 'MORALES', 'SILVA', 
                           'CASTRO', 'ROJAS', 'GALLARDO']
        
        palabras = texto.split()
        if len(palabras) >= 2:  # Al menos nombre y apellido
            for nombre in nombres_comunes:
                if nombre in texto:
                    return True
            for apellido in apellidos_comunes:
                if apellido in texto:
                    return True
        
        return False
    
    # Verificar si es una transferencia personal
    if (es_nombre_persona(detalle_upper) or 
        es_nombre_persona(nombre_destino_upper) or 
        es_nombre_persona(comentario_upper)):
        return 'Transferencias'
    
    categorias = definir_categorias()
    
    # Revisar si el detalle coincide con alguna de las categorías
    for categoria, palabras_clave in categorias.items():
        for palabra in palabras_clave:
            if palabra in detalle_upper:
                return categoria
    
    # Si no coincide ninguna palabra clave, intentar con el nombre del destino
    for categoria, palabras_clave in categorias.items():
        for palabra in palabras_clave:
            if palabra in nombre_destino_upper:
                return categoria
    
    # Por último, intentar con el comentario
    for categoria, palabras_clave in categorias.items():
        for palabra in palabras_clave:
            if palabra in comentario_upper:
                return categoria
    
    return 'Sin categorizar'


def aplicar_categorizacion(df):
    """
    Función que recorre cada fila del DataFrame y asigna la categoría correspondiente
    basándose en múltiples campos (detalle, nombre_destino, comentario).
    Específicamente optimizada para datos TEF bancarios.
    """
    if 'detalle' not in df.columns:
        raise Exception("El DataFrame debe contener la columna 'detalle'")
    
    def categorizar_fila(row):
        # Obtener valores de múltiples campos para una categorización más precisa
        detalle = str(row.get('detalle', ''))
        nombre_destino = str(row.get('nombre_destino', ''))
        comentario = str(row.get('comentario', ''))
        monto = row.get('monto', 0)
        
        return categorizar_transaccion(detalle, nombre_destino, comentario, monto)
    
    # Aplicar categorización a cada fila
    df['categoria'] = df.apply(categorizar_fila, axis=1)
    
    return df


def obtener_resumen_categorias(df):
    """
    Función auxiliar para obtener un resumen de las categorías asignadas.
    Útil para verificar la distribución de categorías.
    """
    if 'categoria' not in df.columns:
        raise Exception("El DataFrame debe contener la columna 'categoria'")
    
    resumen = df.groupby(['categoria', 'tipo']).agg({
        'monto': ['count', 'sum']
    }).round(2)
    
    return resumen


def obtener_reglas_categorizacion():
    """
    Devuelve las reglas de categorización en un formato amigable para el frontend.
    """
    categorias = definir_categorias()
    
    reglas = []
    for categoria, palabras_clave in categorias.items():
        reglas.append({
            'categoria': categoria,
            'palabras_clave': palabras_clave,
            'descripcion': f"Si el detalle contiene alguna de estas palabras: {', '.join(palabras_clave[:5])}{'...' if len(palabras_clave) > 5 else ''}",
            'total_palabras': len(palabras_clave)
        })
    
    return reglas

def sugerir_categoria_para_detalle(detalle):
    """
    Sugiere una categoría para un detalle específico basado en coincidencias parciales.
    
    Args:
        detalle: Texto del detalle de la transacción
    
    Returns:
        Lista de sugerencias con score de confianza
    """
    if not detalle:
        return []
    
    categorias = definir_categorias()
    detalle_upper = detalle.upper()
    sugerencias = []
    
    for categoria, palabras_clave in categorias.items():
        coincidencias = []
        for palabra in palabras_clave:
            if palabra in detalle_upper:
                coincidencias.append(palabra)
        
        if coincidencias:
            # Calcular score basado en número de coincidencias y longitud de palabras
            score = len(coincidencias) * 10 + sum(len(p) for p in coincidencias)
            sugerencias.append({
                'categoria': categoria,
                'score': score,
                'palabras_encontradas': coincidencias,
                'confianza': 'alta' if len(coincidencias) > 1 else 'media'
            })
    
    # Ordenar por score descendente
    sugerencias.sort(key=lambda x: x['score'], reverse=True)
    return sugerencias[:3]  # Retornar top 3 sugerencias

def sugerir_categoria(detalle):
    """
    Sugiere una categoría para una transacción sin categorizar.
    
    Args:
        detalle: Texto del detalle de la transacción
    
    Returns:
        dict con la mejor sugerencia o None si no hay sugerencias
    """
    sugerencias = sugerir_categoria_para_detalle(detalle)
    
    if not sugerencias:
        return None
    
    # Retornar la mejor sugerencia
    mejor_sugerencia = sugerencias[0]
    return {
        'categoria_sugerida': mejor_sugerencia['categoria'],
        'confianza': mejor_sugerencia['confianza'],
        'palabras_encontradas': mejor_sugerencia['palabras_encontradas'],
        'score': mejor_sugerencia['score']
    }

def obtener_coincidencias_parciales(detalle, umbral_coincidencia=0.6):
    """
    Encuentra coincidencias parciales usando similitud de texto.
    
    Args:
        detalle: Texto del detalle de la transacción
        umbral_coincidencia: Umbral mínimo de similitud (0.0 a 1.0)
    
    Returns:
        Lista de categorías con similitud parcial
    """
    import difflib
    
    if not detalle:
        return []
    
    categorias = definir_categorias()
    detalle_words = detalle.upper().split()
    sugerencias_parciales = []
    
    for categoria, palabras_clave in categorias.items():
        for palabra_clave in palabras_clave:
            # Verificar similitud con cada palabra del detalle
            for detalle_word in detalle_words:
                similitud = difflib.SequenceMatcher(
                    None, palabra_clave, detalle_word
                ).ratio()
                
                if similitud >= umbral_coincidencia:
                    sugerencias_parciales.append({
                        'categoria': categoria,
                        'palabra_clave': palabra_clave,
                        'palabra_detalle': detalle_word,
                        'similitud': similitud,
                        'confianza': 'baja' if similitud < 0.8 else 'media'
                    })
    
    # Eliminar duplicados y ordenar por similitud
    sugerencias_unicas = {}
    for sug in sugerencias_parciales:
        key = sug['categoria']
        if key not in sugerencias_unicas or sug['similitud'] > sugerencias_unicas[key]['similitud']:
            sugerencias_unicas[key] = sug
    
    # Convertir a lista y ordenar
    resultado = list(sugerencias_unicas.values())
    resultado.sort(key=lambda x: x['similitud'], reverse=True)
    
    return resultado[:5]  # Top 5 sugerencias

def analizar_transacciones_sin_categorizar(df):
    """
    Analiza todas las transacciones sin categorizar y genera sugerencias.
    
    Args:
        df: DataFrame con transacciones
    
    Returns:
        dict con análisis y sugerencias
    """
    if df.empty:
        return {
            'total_sin_categorizar': 0,
            'monto_total': 0,
            'con_sugerencias': 0,
            'sin_sugerencias': 0,
            'sugerencias_por_categoria': {}
        }
    
    sin_categorizar = df[df['categoria'] == 'Sin categorizar']
    
    if sin_categorizar.empty:
        return {
            'total_sin_categorizar': 0,
            'monto_total': 0,
            'con_sugerencias': 0,
            'sin_sugerencias': 0,
            'sugerencias_por_categoria': {}
        }
    
    con_sugerencias = 0
    sin_sugerencias = 0
    sugerencias_por_categoria = {}
    
    for _, row in sin_categorizar.iterrows():
        sugerencia = sugerir_categoria(row['detalle'])
        
        if sugerencia:
            con_sugerencias += 1
            categoria_sug = sugerencia['categoria_sugerida']
            
            if categoria_sug not in sugerencias_por_categoria:
                sugerencias_por_categoria[categoria_sug] = {
                    'count': 0,
                    'monto_total': 0,
                    'ejemplos': []
                }
            
            sugerencias_por_categoria[categoria_sug]['count'] += 1
            sugerencias_por_categoria[categoria_sug]['monto_total'] += row['monto']
            
            if len(sugerencias_por_categoria[categoria_sug]['ejemplos']) < 3:
                sugerencias_por_categoria[categoria_sug]['ejemplos'].append({
                    'detalle': row['detalle'],
                    'monto': row['monto'],
                    'confianza': sugerencia['confianza']
                })
        else:
            sin_sugerencias += 1
    
    return {
        'total_sin_categorizar': len(sin_categorizar),
        'monto_total': sin_categorizar['monto'].sum(),
        'con_sugerencias': con_sugerencias,
        'sin_sugerencias': sin_sugerencias,
        'sugerencias_por_categoria': sugerencias_por_categoria
    }

# Hacer disponibles las funciones principales
CATEGORIA_KEYWORDS = definir_categorias()

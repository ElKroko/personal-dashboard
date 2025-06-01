from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd
import os

Base = declarative_base()


class Transaccion(Base):
    """
    Modelo SQLAlchemy para la tabla transacciones.
    Campos: fecha, detalle, monto, tipo, categoria, año, mes, semana, tipo_regla, fecha_modificacion.
    """
    __tablename__ = 'transacciones'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    detalle = Column(String(500), nullable=False)
    monto = Column(Float, nullable=False)
    tipo = Column(String(50), nullable=False)
    categoria = Column(String(100), nullable=False)
    año = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    dia = Column(Integer, nullable=False)
    semana = Column(Integer, nullable=False)
    tipo_regla = Column(String(100), default="mapeo_por_palabra_clave")
    created_at = Column(DateTime, default=datetime.now)
    fecha_modificacion = Column(DateTime, default=datetime.now)
    
    def to_dict(self):
        """Convierte la instancia a diccionario"""
        return {
            'id': self.id,
            'fecha': self.fecha.strftime('%Y-%m-%d') if self.fecha else None,
            'detalle': self.detalle,
            'monto': self.monto,
            'tipo': self.tipo,
            'categoria': self.categoria,
            'año': self.año,
            'mes': self.mes,
            'dia': self.dia,
            'semana': self.semana,
            'tipo_regla': self.tipo_regla,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'fecha_modificacion': self.fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_modificacion else None
        }


class CategoriaCustom(Base):
    """
    Modelo SQLAlchemy para categorías personalizadas.
    Permite a los usuarios agregar sus propias categorías y palabras clave.
    """
    __tablename__ = 'categorias_custom'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_categoria = Column(String(100), nullable=False, unique=True)
    palabras_clave = Column(String(1000), nullable=False)  # JSON string con lista de palabras
    descripcion = Column(String(500))
    activa = Column(Integer, default=1)  # 1 = activa, 0 = inactiva
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    
    def to_dict(self):
        """Convierte la instancia a diccionario"""
        import json
        return {
            'id': self.id,
            'nombre_categoria': self.nombre_categoria,
            'palabras_clave': json.loads(self.palabras_clave) if self.palabras_clave else [],
            'descripcion': self.descripcion,
            'activa': bool(self.activa),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class DatabaseManager:
    """
    Clase para manejar la base de datos SQLite.
    """
    
    def __init__(self, db_path="data/finanzas.db"):
        """
        Inicializa la conexión a la base de datos.
        """
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def guardar_dataframe(self, df, modo='append'):
        """
        Guarda un DataFrame en la base de datos.
        
        Args:
            df: DataFrame con las transacciones procesadas
            modo: 'append' para agregar, 'replace' para reemplazar todo
        """
        try:
            if modo == 'replace':
                # Borrar todas las transacciones existentes
                self.session.query(Transaccion).delete()
                self.session.commit()
            
            # Convertir DataFrame a registros
            for _, row in df.iterrows():
                # Verificar si ya existe (para evitar duplicados en modo append)
                if modo == 'append':
                    existe = self.session.query(Transaccion).filter(
                        Transaccion.fecha == row['fecha'].date(),
                        Transaccion.detalle == row['detalle'],
                        Transaccion.monto == row['monto'],
                        Transaccion.tipo == row['tipo']
                    ).first()
                    
                    if existe:
                        continue  # Saltar si ya existe
                
                # Crear nueva transacción
                # Determinar tipo_regla basado en si la categoría es "Sin categorizar"
                tipo_regla = "sin_coincidencias" if row['categoria'] == "Sin categorizar" else "mapeo_por_palabra_clave"
                
                transaccion = Transaccion(
                    fecha=row['fecha'].date(),
                    detalle=row['detalle'],
                    monto=row['monto'],
                    tipo=row['tipo'],
                    categoria=row['categoria'],
                    año=row['año'],
                    mes=row['mes'],
                    dia=row['dia'],
                    semana=row['semana'],
                    tipo_regla=tipo_regla
                )
                
                self.session.add(transaccion)
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error al guardar en base de datos: {str(e)}")
    
    def obtener_todas_transacciones(self):
        """
        Obtiene todas las transacciones de la base de datos.
        Retorna un DataFrame.
        """
        try:
            transacciones = self.session.query(Transaccion).all()
            
            if not transacciones:
                return pd.DataFrame()
            
            # Convertir a DataFrame
            data = [t.to_dict() for t in transacciones]
            df = pd.DataFrame(data)
            
            # Convertir fecha a datetime
            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'])
            
            return df
            
        except Exception as e:
            raise Exception(f"Error al obtener transacciones: {str(e)}")
    
    def obtener_transacciones_por_periodo(self, año=None, mes=None):
        """
        Obtiene transacciones filtradas por período.
        """
        try:
            query = self.session.query(Transaccion)
            
            if año:
                query = query.filter(Transaccion.año == año)
            
            if mes:
                query = query.filter(Transaccion.mes == mes)
            
            transacciones = query.all()
            
            if not transacciones:
                return pd.DataFrame()
            
            # Convertir a DataFrame
            data = [t.to_dict() for t in transacciones]
            df = pd.DataFrame(data)
            
            # Convertir fecha a datetime
            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'])
            
            return df
            
        except Exception as e:
            raise Exception(f"Error al obtener transacciones por período: {str(e)}")
    
    def contar_transacciones(self):
        """
        Cuenta el total de transacciones en la base de datos.
        """
        try:
            return self.session.query(Transaccion).count()
        except Exception as e:
            raise Exception(f"Error al contar transacciones: {str(e)}")
    
    def limpiar_base_datos(self):
        """
        Elimina todas las transacciones de la base de datos.
        """
        try:
            self.session.query(Transaccion).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error al limpiar base de datos: {str(e)}")
    
    def cerrar_conexion(self):
        """
        Cierra la conexión a la base de datos.
        """
        self.session.close()
    
    def actualizar_categoria_transaccion(self, transaccion_id, nueva_categoria):
        """
        Actualiza la categoría de una transacción específica.
        
        Args:
            transaccion_id: ID de la transacción a actualizar
            nueva_categoria: Nueva categoría a asignar
        
        Returns:
            Transacción actualizada o None si no se encuentra
        """
        try:
            transaccion = self.session.query(Transaccion).filter(
                Transaccion.id == transaccion_id
            ).first()
            
            if not transaccion:
                return None
            
            transaccion.categoria = nueva_categoria
            transaccion.tipo_regla = "sobrescritura_manual"
            transaccion.fecha_modificacion = datetime.now()
            
            self.session.commit()
            return transaccion.to_dict()
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error al actualizar categoría: {str(e)}")
    
    def obtener_transacciones_filtradas(self, fecha_desde=None, fecha_hasta=None, 
                                      categoria=None, tipo_movimiento=None, 
                                      texto_busqueda=None, limit=None, offset=0):
        """
        Obtiene transacciones con filtros específicos.
        
        Args:
            fecha_desde: Fecha mínima (formato YYYY-MM-DD)
            fecha_hasta: Fecha máxima (formato YYYY-MM-DD)
            categoria: Categoría específica
            tipo_movimiento: 'INGRESO' o 'GASTO'
            texto_busqueda: Texto a buscar en el campo detalle
            limit: Número máximo de resultados
            offset: Número de registros a saltar (paginación)
        
        Returns:
            Lista de transacciones filtradas
        """
        try:
            query = self.session.query(Transaccion)
            
            # Filtro por fecha
            if fecha_desde:
                query = query.filter(Transaccion.fecha >= fecha_desde)
            if fecha_hasta:
                query = query.filter(Transaccion.fecha <= fecha_hasta)
            
            # Filtro por categoría
            if categoria:
                query = query.filter(Transaccion.categoria == categoria)
            
            # Filtro por tipo de movimiento
            if tipo_movimiento:
                query = query.filter(Transaccion.tipo == tipo_movimiento)
            
            # Filtro por texto en detalle
            if texto_busqueda:
                query = query.filter(Transaccion.detalle.contains(texto_busqueda))
            
            # Ordenar por fecha descendente
            query = query.order_by(Transaccion.fecha.desc())
            
            # Paginación
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            transacciones = query.all()
            return [t.to_dict() for t in transacciones]
            
        except Exception as e:
            raise Exception(f"Error al obtener transacciones filtradas: {str(e)}")
    
    def contar_transacciones_filtradas(self, fecha_desde=None, fecha_hasta=None, 
                                     categoria=None, tipo_movimiento=None, 
                                     texto_busqueda=None):
        """
        Cuenta transacciones que coinciden con los filtros.
        """
        try:
            query = self.session.query(Transaccion)
            
            # Aplicar los mismos filtros que en obtener_transacciones_filtradas
            if fecha_desde:
                query = query.filter(Transaccion.fecha >= fecha_desde)
            if fecha_hasta:
                query = query.filter(Transaccion.fecha <= fecha_hasta)
            if categoria:
                query = query.filter(Transaccion.categoria == categoria)
            if tipo_movimiento:
                query = query.filter(Transaccion.tipo == tipo_movimiento)
            if texto_busqueda:
                query = query.filter(Transaccion.detalle.contains(texto_busqueda))
            
            return query.count()
            
        except Exception as e:
            raise Exception(f"Error al contar transacciones filtradas: {str(e)}")
    
    def obtener_resumen_por_categorias(self, fecha_desde=None, fecha_hasta=None):
        """
        Obtiene un resumen de totales agrupados por categoría.
        
        Returns:
            Lista de diccionarios con categoria, total_ingresos, total_gastos
        """
        try:
            from sqlalchemy import func
            
            query = self.session.query(
                Transaccion.categoria,
                func.sum(func.case([(Transaccion.tipo == 'INGRESO', Transaccion.monto)], else_=0)).label('total_ingresos'),
                func.sum(func.case([(Transaccion.tipo == 'GASTO', Transaccion.monto)], else_=0)).label('total_gastos')
            )
            
            # Filtros de fecha
            if fecha_desde:
                query = query.filter(Transaccion.fecha >= fecha_desde)
            if fecha_hasta:
                query = query.filter(Transaccion.fecha <= fecha_hasta)
            
            # Agrupar por categoría
            query = query.group_by(Transaccion.categoria)
            
            resultados = query.all()
            
            return [
                {
                    'categoria': resultado.categoria,
                    'total_ingresos': float(resultado.total_ingresos or 0),
                    'total_gastos': float(resultado.total_gastos or 0),
                    'total_neto': float((resultado.total_ingresos or 0) - (resultado.total_gastos or 0))
                }
                for resultado in resultados
            ]
            
        except Exception as e:
            raise Exception(f"Error al obtener resumen por categorías: {str(e)}")
    
    def obtener_categorias_disponibles(self):
        """
        Obtiene todas las categorías únicas disponibles en la base de datos.
        """
        try:
            from sqlalchemy import distinct
            
            categorias = self.session.query(distinct(Transaccion.categoria)).all()
            return [categoria[0] for categoria in categorias]
            
        except Exception as e:
            raise Exception(f"Error al obtener categorías disponibles: {str(e)}")
    
    # =================== MÉTODOS PARA CATEGORÍAS PERSONALIZADAS ===================
    
    def obtener_categorias_custom(self):
        """
        Obtiene todas las categorías personalizadas activas.
        """
        try:
            categorias = self.session.query(CategoriaCustom).filter(
                CategoriaCustom.activa == 1
            ).all()
            return [categoria.to_dict() for categoria in categorias]
            
        except Exception as e:
            raise Exception(f"Error al obtener categorías personalizadas: {str(e)}")
    
    def crear_categoria_custom(self, nombre_categoria, palabras_clave, descripcion=""):
        """
        Crea una nueva categoría personalizada.
        
        Args:
            nombre_categoria: Nombre de la categoría
            palabras_clave: Lista de palabras clave
            descripcion: Descripción opcional
        """
        try:
            import json
            from datetime import datetime
            
            # Verificar si ya existe
            existe = self.session.query(CategoriaCustom).filter(
                CategoriaCustom.nombre_categoria == nombre_categoria
            ).first()
            
            if existe:
                raise Exception(f"La categoría '{nombre_categoria}' ya existe")
            
            # Crear nueva categoría
            nueva_categoria = CategoriaCustom(
                nombre_categoria=nombre_categoria,
                palabras_clave=json.dumps(palabras_clave, ensure_ascii=False),
                descripcion=descripcion,
                activa=1,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.session.add(nueva_categoria)
            self.session.commit()
            
            return nueva_categoria.to_dict()
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error al crear categoría personalizada: {str(e)}")
    
    def actualizar_categoria_custom(self, categoria_id, nombre_categoria=None, palabras_clave=None, descripcion=None):
        """
        Actualiza una categoría personalizada existente.
        
        Args:
            categoria_id: ID de la categoría a actualizar
            nombre_categoria: Nuevo nombre (opcional)
            palabras_clave: Nueva lista de palabras clave (opcional)
            descripcion: Nueva descripción (opcional)
        """
        try:
            import json
            from datetime import datetime
            
            categoria = self.session.query(CategoriaCustom).filter(
                CategoriaCustom.id == categoria_id
            ).first()
            
            if not categoria:
                raise Exception(f"Categoría con ID {categoria_id} no encontrada")
            
            # Actualizar campos si se proporcionan
            if nombre_categoria is not None:
                # Verificar que no exista otra categoría con el mismo nombre
                existe = self.session.query(CategoriaCustom).filter(
                    CategoriaCustom.nombre_categoria == nombre_categoria,
                    CategoriaCustom.id != categoria_id
                ).first()
                
                if existe:
                    raise Exception(f"Ya existe otra categoría con el nombre '{nombre_categoria}'")
                
                categoria.nombre_categoria = nombre_categoria
            
            if palabras_clave is not None:
                categoria.palabras_clave = json.dumps(palabras_clave, ensure_ascii=False)
            
            if descripcion is not None:
                categoria.descripcion = descripcion
            
            categoria.updated_at = datetime.now()
            
            self.session.commit()
            return categoria.to_dict()
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error al actualizar categoría personalizada: {str(e)}")
    
    def eliminar_categoria_custom(self, categoria_id):
        """
        Elimina (marca como inactiva) una categoría personalizada.
        
        Args:
            categoria_id: ID de la categoría a eliminar
        """
        try:
            from datetime import datetime
            
            categoria = self.session.query(CategoriaCustom).filter(
                CategoriaCustom.id == categoria_id
            ).first()
            
            if not categoria:
                raise Exception(f"Categoría con ID {categoria_id} no encontrada")
            
            categoria.activa = 0
            categoria.updated_at = datetime.now()
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error al eliminar categoría personalizada: {str(e)}")
    
    def obtener_todas_categorias_con_custom(self):
        """
        Obtiene todas las categorías (predefinidas + personalizadas) en un formato unificado.
        """
        try:
            # Obtener categorías predefinidas
            from utils.categorizar import definir_categorias
            categorias_predefinidas = definir_categorias()
            
            # Obtener categorías personalizadas
            categorias_custom = self.obtener_categorias_custom()
            
            # Combinar en formato unificado
            todas_categorias = {}
            
            # Agregar predefinidas
            for nombre, palabras in categorias_predefinidas.items():
                todas_categorias[nombre] = {
                    'tipo': 'predefinida',
                    'palabras_clave': palabras,
                    'descripcion': f'Categoría predefinida del sistema',
                    'editable': False
                }
            
            # Agregar personalizadas
            for categoria in categorias_custom:
                todas_categorias[categoria['nombre_categoria']] = {
                    'tipo': 'personalizada',
                    'id': categoria['id'],
                    'palabras_clave': categoria['palabras_clave'],
                    'descripcion': categoria['descripcion'],
                    'editable': True,
                    'created_at': categoria['created_at'],
                    'updated_at': categoria['updated_at']
                }
            
            return todas_categorias
            
        except Exception as e:
            raise Exception(f"Error al obtener todas las categorías: {str(e)}")

# Dashboard Financiero Personal

Un dashboard moderno y completo para análisis de finanzas personales construido con **Astro** (frontend) y **FastAPI** (backend).

## 🚀 Características

### 📊 Análisis Completo
- **Vista General**: Indicadores principales con gráficos de ingresos vs gastos y distribución por categorías
- **Análisis Mensual**: Evolución mensual de ingresos, gastos y balance
- **Análisis Semanal**: Desglose semanal con análisis detallado por mes
- **Análisis Diario**: Vista diaria con transacciones detalladas y balance acumulado

### 📈 Visualizaciones
- Gráficos de barras para comparar ingresos y gastos
- Gráficos de líneas para mostrar evolución del balance
- Gráficos de dona para distribución por categorías
- Tablas interactivas con datos detallados

### 🔧 Funcionalidades
- **Carga de archivos Excel**: Procesamiento automático de transacciones
- **Categorización automática**: Clasificación inteligente de transacciones
- **Filtros de fecha**: Análisis por año, mes y períodos personalizados
- **Responsive design**: Optimizado para desktop y móvil
- **Persistencia opcional**: Base de datos SQLite para historial

## 🏗️ Arquitectura

### Frontend (Astro + React)
- **Framework**: Astro 5.x con integración React
- **Componentes**: React con hooks para estado y efectos
- **Gráficos**: Chart.js para visualizaciones interactivas
- **Estilos**: CSS moderno con variables y grid/flexbox
- **Build**: Optimización automática y generación estática

### Backend (FastAPI + Python)
- **Framework**: FastAPI para API REST
- **Procesamiento**: Pandas para análisis de datos
- **Base de datos**: SQLAlchemy con SQLite (opcional)
- **Excel**: Openpyxl para lectura de archivos
- **CORS**: Configurado para desarrollo local

## 📁 Estructura del Proyecto

```
mi-dashboard-finanzas-astro/
├── backend/
│   ├── app.py                 # Servidor FastAPI principal
│   ├── requirements.txt       # Dependencias Python
│   ├── data/                 # Datos procesados y BD
│   └── utils/
│       ├── leer_excel.py     # Lectura de archivos Excel
│       ├── categorizar.py    # Categorización automática
│       ├── fechas.py         # Manejo de fechas
│       ├── agregaciones.py   # Cálculos y estadísticas
│       └── bd.py            # Base de datos (opcional)
└── frontend/
    ├── src/
    │   ├── components/       # Componentes React
    │   │   ├── UploadForm.jsx    # Formulario de carga
    │   │   ├── Indicadores.jsx   # Vista general
    │   │   ├── Mensual.jsx       # Análisis mensual
    │   │   ├── Semanal.jsx       # Análisis semanal
    │   │   └── Diario.jsx        # Análisis diario
    │   ├── layouts/
    │   │   └── MainLayout.astro  # Layout principal
    │   └── pages/               # Páginas Astro
    │       ├── index.astro      # Página principal
    │       ├── mensual.astro    # Página mensual
    │       ├── semanal.astro    # Página semanal
    │       └── diario.astro     # Página diaria
    ├── public/
    │   └── styles.css           # Estilos globales
    └── package.json
```

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Python 3.12+
- Node.js 18+
- npm o yarn

### 1. Configurar Backend

```bash
# Navegar al directorio backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Configurar Frontend

```bash
# Navegar al directorio frontend
cd frontend

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
npm run dev

# O construir para producción
npm run build
```

### 3. Acceder a la Aplicación

- **Frontend**: http://localhost:4321
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

## 📊 API Endpoints

### POST `/procesar/`
Procesa un archivo Excel y devuelve estadísticas básicas.

**Request**: Archivo Excel (multipart/form-data)
**Response**: 
```json
{
  "mensaje": "Archivo procesado exitosamente",
  "total_transacciones": 150,
  "rango_fechas": "2024-01-01 a 2024-12-31"
}
```

### GET `/historial/`
Obtiene todas las transacciones procesadas.

**Response**: Array de transacciones con datos enriquecidos (categoría, fecha formateada, etc.)

### GET `/stats/`
Obtiene estadísticas agregadas de todas las transacciones.

**Response**:
```json
{
  "total_ingresos": 5000.00,
  "total_gastos": -3000.00,
  "total_transacciones": 150,
  "por_categoria": {
    "Alimentación": -800.00,
    "Salario": 5000.00,
    "Transporte": -400.00
  }
}
```

## 📱 Vistas y Funcionalidades

### 🏠 Vista Principal (/)
- Formulario de carga de archivos Excel
- Indicadores generales (ingresos, gastos, balance, transacciones)
- Gráfico de barras: Ingresos vs Gastos
- Gráfico de dona: Distribución por categorías
- Tabla detallada por categorías

### 📅 Vista Mensual (/mensual)
- Selector de año
- Resumen anual (ingresos, gastos, balance, transacciones)
- Gráfico de barras: Ingresos vs Gastos por mes
- Gráfico de líneas: Evolución del balance mensual
- Tabla detallada mensual

### 📆 Vista Semanal (/semanal)
- Selectores de año y mes
- Resumen mensual
- Gráfico de barras: Ingresos vs Gastos por semana
- Gráfico de líneas: Evolución del balance semanal
- Tabla detallada semanal con rangos de fechas

### 📊 Vista Diaria (/diario)
- Selector de fecha inicial y rango de días (7, 14, 30 días)
- Resumen del período seleccionado
- Gráfico de barras: Ingresos vs Gastos diarios
- Gráfico de líneas: Balance acumulado
- Tabla detallada diaria
- Tabla de transacciones del día seleccionado

## 🎨 Características del Diseño

### 🌈 Sistema de Colores
- **Ingresos**: Verde (#4CAF50)
- **Gastos**: Rojo (#f44336)
- **Neutro**: Azul (#2196F3)
- **Fondo**: Gris claro (#f5f6fa)

### 📐 Layout Responsivo
- **Desktop**: Grid de 2-4 columnas para tarjetas y gráficos
- **Tablet**: Grid de 2 columnas
- **Móvil**: Una columna con elementos apilados

### 🎯 Experiencia de Usuario
- Loading states con animaciones
- Estados de error con mensajes claros
- Navegación intuitiva entre vistas
- Tooltips informativos en gráficos
- Formato de moneda localizado

## 🔧 Configuración Avanzada

### Base de Datos
Por defecto, los datos se almacenan en memoria. Para persistencia:

1. Los datos se guardan automáticamente en SQLite (`data/transacciones.db`)
2. El esquema se crea automáticamente al ejecutar el backend
3. Los datos persisten entre reinicios del servidor

### Categorización
El sistema incluye categorización automática basada en palabras clave. Puedes personalizar las reglas en `utils/categorizar.py`:

```python
CATEGORIA_KEYWORDS = {
    'Alimentación': ['supermercado', 'restaurante', 'comida'],
    'Transporte': ['gasolina', 'bus', 'metro', 'taxi'],
    'Vivienda': ['alquiler', 'electricidad', 'agua', 'gas'],
    # ... más categorías
}
```

## 🐛 Solución de Problemas

### Backend no inicia
- Verificar que el entorno virtual esté activado
- Instalar dependencias: `pip install -r requirements.txt`
- Verificar Python 3.12+

### Frontend no carga gráficos
- Verificar que el backend esté ejecutándose en puerto 8000
- Comprobar CORS en el navegador
- Verificar que Chart.js esté instalado: `npm install chart.js react-chartjs-2`

### Errores de carga de Excel
- Verificar formato del archivo (solo .xlsx soportado)
- Asegurar que las columnas requeridas existan (Fecha, Monto, Descripción)
- Verificar formato de fecha en Excel

## 🚀 Próximas Funcionalidades

- [ ] Filtros avanzados por categoría y rango de montos
- [ ] Exportación de reportes en PDF
- [ ] Configuración de categorías personalizada
- [ ] Comparación entre períodos
- [ ] Predicciones y tendencias
- [ ] Alertas y notificaciones
- [ ] Múltiples cuentas/archivos
- [ ] Dashboard en tiempo real

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu funcionalidad (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias, por favor abre un issue en el repositorio.

---

**Dashboard Financiero Personal** - Desarrollado con ❤️ usando Astro y FastAPI

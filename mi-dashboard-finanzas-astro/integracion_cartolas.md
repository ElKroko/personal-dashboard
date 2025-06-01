Para categorizar tus archivos de cartola (los `.xls` que subiste), el flujo general es:

1. **Detectar dónde empieza la tabla en cada archivo**
2. **Leer cada archivo** capturando la cabecera correcta
3. **Limpiar/normalizar** columnas (fechas, montos, texto)
4. **Concatenar** todas las transacciones en un único DataFrame
5. **Aplicar la función de categorización** que mapea cada descripción a una “categoría”
6. **Revisar y ajustar** posibles transacciones sin categoría (o categorías equivocadas)

A continuación te describo paso a paso cómo hacerlo.

---

## 1. Encontrar el inicio de la tabla en cada `.xls`

Cada uno de tus archivos (`cartola_31012025.xls`, `cartola_28022025.xls`, etc.) viene con varias filas de encabezados o texto antes del bloque de datos. Lo más habitual en las cartolas de Banco de Chile es que la fila donde empieza la tabla contenga el título “Fecha” (o “Fecha Movimiento”) como primera columna, y que justo debajo empiecen las filas transaccionales.

**Estrategia para detectar “dinámicamente” dónde está el header**:

* Leer cada archivo con `pd.read_excel(..., header=None)` durante las primeras 30–40 filas.
* Buscar en esas filas la fila que contenga el texto “Fecha” (u otro nombre exacto de la columna que use tu banco).
* Suponiendo que esa fila es la que define los nombres de columna, la numeramos (por ejemplo, fila 11 si el header está en la posición 11 de 0-based) y luego volvemos a llamar a `pd.read_excel(..., header=11)`.

Este es el algoritmo genérico:

1. **Para cada archivo:**

   ```python
   import pandas as pd

   # 1.1 Leer las primeras 30 filas “a ciegas” (sin header) para inspeccionar
   df_preview = pd.read_excel(ruta_archivo, header=None, nrows=30)

   # 1.2 Buscar en qué fila (índice 0-based) aparece la palabra “Fecha”
   fila_header = None
   for idx, row in df_preview.iterrows():
       # Convierte cada celda a string y busca “Fecha” exacto
       if any(str(cell).strip() == "Fecha" for cell in row):
           fila_header = idx
           break

   if fila_header is None:
       raise ValueError(f"No encontré la fila de 'Fecha' en {ruta_archivo}")

   # 1.3 Ahora que sabemos que el header está en fila_header, leer el DataFrame real
   df = pd.read_excel(ruta_archivo, header=fila_header)

   # 1.4 Eliminar las columnas “Unnamed” que quedaron vacías
   df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
   ```

   — De este modo nos aseguramos, aunque varíe un poco la posición en cada archivo, de apuntar exactamente a la fila donde aparece el título de columna.

---

## 2. Normalizar columnas (limpieza inicial)

Una vez leído cada archivo con su header correcto, tenemos un DataFrame con columnas como “Fecha”, “Detalle” o “Descripción”, “Monto”, “Tipo de movimiento” (o nombres muy parecidos). Conviene renombrarlas a algo estándar y convertir tipos:

```python
# 2.1 Renombrar columnas más descriptivas a nombres sencillos (sin espacios)
df = df.rename(columns={
    "Fecha": "fecha",
    "Fecha Movimiento": "fecha",          # Si en algún archivo aparece así
    "Detalle": "detalle",                  # O “Descripción”
    "Descripción": "detalle",
    "Monto": "monto",
    "Tipo Movimiento": "tipo_movimiento",  # O el nombre exacto que venga
    "Tipo de Movimiento": "tipo_movimiento",
    # (añade más mapeos si tus archivos tienen otras cabeceras)
})

# 2.2 Convertir fecha a datetime y monto a float
df["fecha"] = pd.to_datetime(df["fecha"], dayfirst=True, errors="coerce")
df["monto"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0.0)

# 2.3 Limpiar el texto en “detalle” y “tipo_movimiento”
df["detalle"] = df["detalle"].astype(str).str.strip()
df["tipo_movimiento"] = df["tipo_movimiento"].astype(str).str.strip()

# 2.4 Eliminar filas donde “fecha” sea NaT
df = df.dropna(subset=["fecha"])
```

En cada uno de tus archivos `.xls` debes hacer exactamente eso:

1. Leer con `header=fila_header` (detectado dinámicamente).
2. Eliminar columnas “Unnamed”.
3. Renombrar columnas claves a `fecha`, `detalle`, `monto`, `tipo_movimiento`.
4. Convertir tipos y eliminar filas sin fecha válida.

---

## 3. Concatenar todos los archivos en un solo DataFrame

Imagina que tienes una lista de rutas:

```python
rutas = [
    "/mnt/data/cartola_31012025.xls",
    "/mnt/data/cartola_28022025.xls",
    "/mnt/data/cartola_31032025.xls",
    "/mnt/data/cartola_30042025.xls"
]
```

Creas un bucle que lea cada uno usando el procedimiento anterior y vaya acumulando:

```python
lista_dfs = []
for ruta in rutas:
    # Paso A: detectar fila_header
    df_preview = pd.read_excel(ruta, header=None, nrows=30)
    fila_header = None
    for idx, row in df_preview.iterrows():
        if any(str(cell).strip() == "Fecha" for cell in row):
            fila_header = idx
            break
    if fila_header is None:
        raise ValueError(f"No se encontró 'Fecha' en {ruta}")

    # Paso B: leer con header correcto
    df_temp = pd.read_excel(ruta, header=fila_header)
    df_temp = df_temp.loc[:, ~df_temp.columns.str.contains("^Unnamed")]

    # Paso C: renombrar y normalizar
    df_temp = df_temp.rename(columns={
        "Fecha": "fecha",
        "Fecha Movimiento": "fecha",
        "Detalle": "detalle",
        "Descripción": "detalle",
        "Monto": "monto",
        "Tipo Movimiento": "tipo_movimiento",
        "Tipo de Movimiento": "tipo_movimiento",
    })
    df_temp["fecha"] = pd.to_datetime(df_temp["fecha"], dayfirst=True, errors="coerce")
    df_temp["monto"] = pd.to_numeric(df_temp["monto"], errors="coerce").fillna(0.0)
    df_temp["detalle"] = df_temp["detalle"].astype(str).str.strip()
    df_temp["tipo_movimiento"] = df_temp["tipo_movimiento"].astype(str).str.strip()
    df_temp = df_temp.dropna(subset=["fecha"])

    lista_dfs.append(df_temp)

# Concatenar todos en uno solo
df_todas = pd.concat(lista_dfs, ignore_index=True)
```

Ahora `df_todas` contendrá, en un único DataFrame, todas las transacciones de enero, febrero, marzo y abril de 2025. Sus columnas mínimas son:

```
["fecha", "detalle", "monto", "tipo_movimiento", … (otras que arrastren tus cartolas, por ejemplo “Saldo” si aparece, etc.)]
```

---

## 4. Añadir columnas auxiliares de tiempo (para agrupar más adelante)

Para luego poder calcular resúmenes mensuales, semanales o diarios, añadimos:

```python
df_todas["año"] = df_todas["fecha"].dt.year
df_todas["mes"] = df_todas["fecha"].dt.month
df_todas["semana"] = df_todas["fecha"].dt.isocalendar().week
df_todas["dia"] = df_todas["fecha"].dt.day
```

De esta manera podrás, por ejemplo, hacer:

```python
# Filtrar solo gastos
df_gastos = df_todas[df_todas["monto"] < 0]   # si en tu cartola los gastos vienen con signo negativo
# O
df_ingresos = df_todas[df_todas["monto"] > 0]
```

O agrupar:

```python
# Total de gastos por mes
resumen = df_todas.groupby(["año", "mes"])["monto"].sum().reset_index()
```

---

## 5. Definir la función de categorización

Con la tabla completa en `df_todas`, lo que quieres es asignar a cada fila una “categoría” (ej. “Gasto – Alimentos”, “Ingreso – Sueldos”, “Gasto – Servicios”, etc.) atendiendo al texto que haya en `detalle`. Un método simple es usar un **diccionario de palabras clave** que, si aparecen en `detalle`, mapeen a una categoría.

Por ejemplo:

```python
# 5.1 Diccionario base de palabras clave → categoría
CATEGORIAS = {
    "SUPERMERCADO": "Gasto – Alimentos",
    "RESTAURANT": "Gasto – Alimentos",
    "PANADERÍA": "Gasto – Alimentos",
    "EXPRESS": "Gasto – Transporte",     # por ejemplo, si “TAXI EXPRESS”
    "TAXI": "Gasto – Transporte",
    "METRO": "Gasto – Transporte",
    "PEAJE": "Gasto – Transporte",
    "LAVANDERÍA": "Gasto – Servicios",
    "TELEFONO": "Gasto – Servicios",
    "AGUA": "Gasto – Servicios",
    "LUZ": "Gasto – Servicios",
    "ARRIENDO": "Gasto – Vivienda",
    "HIPOTECA": "Gasto – Vivienda",
    "SUELDO": "Ingreso – Sueldos",
    "ABONO": "Ingreso – Abonos",
    "DIVIDENDO": "Ingreso – Inversiones",
    # … agrega todas las palabras clave que consideres necesarias
}

def asignar_categoria(detalle: str) -> str:
    """
    Busca, en mayúsculas, si alguna de las claves del diccionario
    aparece dentro del texto 'detalle'. Retorna la categoría asociada.
    Si no hay coincidencias, devuelve "Sin categorizar".
    """
    texto = detalle.upper()
    for clave, categoria in CATEGORIAS.items():
        if clave in texto:
            return categoria
    return "Sin categorizar"
```

Luego, para procesar todo el DataFrame:

```python
df_todas["categoria"] = df_todas["detalle"].apply(asignar_categoria)
```

Ahora `df_todas` tendrá una columna extra `"categoria"`. Por ejemplo, si `detalle = "Compra SUPERMERCADO Lider"`, la función encuentra la clave `"SUPERMERCADO"` y asigna `"Gasto – Alimentos"`. Si el detalle no coincide con ninguna palabra clave, marca `"Sin categorizar"`.

---

## 6. Revisar los casos “Sin categorizar” y ajustar

Después de aplicar:

```python
sin_cat = df_todas[df_todas["categoria"] == "Sin categorizar"]
print(f"Hay {len(sin_cat)} transacciones sin categoría.")
# Puedes inspeccionar las primeras 10:
print(sin_cat[["fecha", "detalle", "monto"]].head(10))
```

Suele ocurrir que algunos movimientos tienen detalles muy específicos (por ejemplo, “Pago Netflix Abril” o “RECARGA CLARO”), que aún no estaban en tu diccionario. A medida que mires esos casos, puedes ir agregando nuevas palabras clave:

```python
# Por ejemplo, descubres que Netflix nunca quedaba categorizado:
CATEGORIAS["NETFLIX"] = "Gasto – Entretenimiento"
# Y “CLARO”:
CATEGORIAS["CLARO"] = "Gasto – Telefonía"
```

Y vuelves a correr

```python
df_todas["categoria"] = df_todas["detalle"].apply(asignar_categoria)
```

hasta que el porcentaje de “Sin categorizar” sea tolerable.

---

## 7. Función completa para ETL + categorización sobre todos los archivos

Reuniendo todo, podrías tener un único script que:

1. Recibe una lista de rutas a los `.xls`.
2. Por cada uno: detecta la fila donde está “Fecha”, lee con ese header, limpia columnas y convierte tipos.
3. Concatena todos los DataFrames en `df_todas`.
4. Añade columnas de tiempo (año, mes, semana, día).
5. Aplica la función `asignar_categoria` sobre `detalle`.
6. Retorna (o guarda en disco / en base de datos) el DataFrame ya categorizado.

Por ejemplo, en pseudo-código:

```python
import pandas as pd

CATEGORIAS = {
    # … llena tu diccionario de palabra_clave → categoría …
}

def asignar_categoria(detalle: str) -> str:
    texto = detalle.upper()
    for clave, categoria in CATEGORIAS.items():
        if clave in texto:
            return categoria
    return "Sin categorizar"

def procesar_archivos_cartola(lista_rutas: list) -> pd.DataFrame:
    acumulador = []
    for ruta in lista_rutas:
        # 1. Leer primero la parte de preview para detectar header
        preview = pd.read_excel(ruta, header=None, nrows=30)
        fila_header = None
        for idx, row in preview.iterrows():
            if any(str(cell).strip() == "Fecha" for cell in row):
                fila_header = idx
                break
        if fila_header is None:
            raise ValueError(f"No se encontró la fila de 'Fecha' en {ruta}")

        # 2. Leer con esa fila como header
        df = pd.read_excel(ruta, header=fila_header)
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        # 3. Renombrar y limpiar
        df = df.rename(columns={
            "Fecha": "fecha",
            "Fecha Movimiento": "fecha",
            "Detalle": "detalle",
            "Descripción": "detalle",
            "Monto": "monto",
            "Tipo Movimiento": "tipo_movimiento",
            "Tipo de Movimiento": "tipo_movimiento",
        })
        df["fecha"] = pd.to_datetime(df["fecha"], dayfirst=True, errors="coerce")
        df["monto"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0.0)
        df["detalle"] = df["detalle"].astype(str).str.strip()
        df["tipo_movimiento"] = df["tipo_movimiento"].astype(str).str.strip()
        df = df.dropna(subset=["fecha"])

        acumulador.append(df)

    # 4. Concatenar todo
    df_todas = pd.concat(acumulador, ignore_index=True)

    # 5. Columnas auxiliares de tiempo
    df_todas["año"] = df_todas["fecha"].dt.year
    df_todas["mes"] = df_todas["fecha"].dt.month
    df_todas["semana"] = df_todas["fecha"].dt.isocalendar().week
    df_todas["dia"] = df_todas["fecha"].dt.day

    # 6. Asignar categoría
    df_todas["categoria"] = df_todas["detalle"].apply(asignar_categoria)

    return df_todas

# Uso:
rutas_cartolas = [
    "/mnt/data/cartola_31012025.xls",
    "/mnt/data/cartola_28022025.xls",
    "/mnt/data/cartola_31032025.xls",
    "/mnt/data/cartola_30042025.xls",
]
df_categorizado = procesar_archivos_cartola(rutas_cartolas)

# Ver cuántas filas quedan y cuántas sin categorizar
print("Total transacciones:", len(df_categorizado))
print("Sin categorizar:", len(df_categorizado[df_categorizado["categoria"] == "Sin categorizar"]))

# Mostrar ejemplo
print(df_categorizado.head(10))
```

---

## 8. Qué hacer después de tener todo en un solo DataFrame

Una vez que ya tienes `df_categorizado` con la columna `"categoria"`, tu siguiente paso (si lo quieres integrar en tu dashboard Astro/FastAPI) será:

1. **Guardar** ese DataFrame (o bien enviar los datos ya categorizados a la base de datos).
2. **Exponer** en tu API un endpoint (por ejemplo, `/transacciones/`) que devuelva “fecha, detalle, monto, tipo\_movimiento, categoría, año, mes, semana” en JSON.
3. El frontend (Astro/React) simplemente hará fetch a ese endpoint para poblar tablas y gráficos filtrando por categoría, mes, etc.

En términos de ‘ETL’ puro, este script ya hace el “E” (extracción), el “T” (transformación: limpieza y categorización) y deja listo el “L” (carga) si decides volcarlo a una BD o un archivo parquet/CSV.

---

## 9. Ajustes finales y buenas prácticas

* **Mantén actualizado el diccionario `CATEGORIAS`**: cada vez que veas un detalle nuevo que sale en “Sin categorizar”, agrégalo (por ejemplo, “PAYPAL” → “Gasto – Servicios”, “UBER” → “Gasto – Transporte”, etc.).
* **Normalización de mayúsculas/minúsculas**: al convertir todo a `detalle.upper()`, evitas errores por “netflix” vs. “Netflix”.
* **Columnas adicionales**: si tus cartolas incluyen campos extra (por ejemplo, “Saldo” o “Observaciones”), puedes dejarlos y luego decidir si quieres mostrarlos en el dashboard.
* **Separar script de ETL**: guárdalo en un archivo independiente (por ejemplo, `etl_cartolas.py`). Así, cuando llegue un nuevo archivo cada mes, solo actualizas la ruta y vuelves a ejecutarlo.
* **Automatización en FastAPI**: podrías exponer una ruta `/upload_cartola/` que reciba los `.xls` y ejecute `procesar_archivos_cartola([…])` en tiempo real, devolviendo directamente el DataFrame ya categorizado como JSON.

---

Con este flujo tendrás todos tus archivos de enero, febrero, marzo y abril de 2025 unidos en un único DataFrame limpio y con una columna “categoria” aplicada. A partir de ahí puedes generar resúmenes por categoría, por mes, por semana o crear cualquier métrica adicional (por ejemplo, “¿cuánto gasté en ‘Gasto – Alimentos’ en abril?”).

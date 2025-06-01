A continuación tienes un plan detallado para enriquecer tu dashboard, de manera que puedas:

1. Visualizar de forma transparente **cómo se están asignando las categorías**.
2. Ver exactamente **en qué te estás gastando el dinero** (desglose por categoría, por monto, fechas, etc.).
3. **Editar manualmente** la categoría propuesta para cada transacción directamente desde la interfaz y que ese cambio se refleje en los informes acumulados.

El objetivo es transformar tu dashboard en una herramienta verdaderamente interactiva y comprensible, donde no solo veas cifras, sino también el razonamiento detrás de cada etiquetado y la posibilidad de corregirlo “sobre la marcha”.

---

## 1. Mostrar la lógica de categorización y transparencia de las reglas

### 1.1. Visor / documentación en el dashboard

* Crea una sección (o modal desplegable) llamada “¿Cómo funcionan las categorías?” donde expliques, de forma resumida y amigable, las **reglas de asignación**. Por ejemplo:

  * “Si la descripción de la transacción contiene la palabra ‘SUPERMERCADO’, se asigna categoría ‘Gasto – Alimentos’.”
  * “Si aparece ‘SUELDO’, va a ‘Ingreso – Sueldos’.”
  * Y así sucesivamente.
* Este texto puede ser estático o bien, generarse dinámicamente a partir del propio diccionario de palabras clave en tu backend. De ese modo, si tú agregas o modificas reglas, el dashboard leerá siempre la versión actualizada del diccionario.

### 1.2. Indicador de “confianza” o “tipo de regla” para cada transacción

* Al procesar cada transacción en el backend, agrega un campo extra (por ejemplo, `tipo_regla`) que describa **por qué** se le asignó esa categoría:

  * `"mapeo_por_palabra_clave"` si la clave apareció literalmente en el texto.
  * `"sobrescritura_manual"` si antes hubo un ajuste manual.
  * `"sin_coincidencias"` si se colocó en “Sin categorizar”.
* En la tabla de “Detalle por transacciones” de tu dashboard, añade una columna pequeña que muestre ese `tipo_regla`. Así podrás identificar rápidamente:

  * Los movimientos que fueron categorizados automáticamente por una palabra clave (verde, por ejemplo).
  * Los que se están cuadrando manualmente (ícono de lápiz).
  * Los que están “sin categorizar” (ícono de alerta).

De esta forma, no tendrás que adivinar por qué un gasto terminó en “Gasto – Servicios”; verás directamente “mapeo\_por\_palabra\_clave” y, al pasar el cursor, sabrás qué palabra exacta emparejó.

---

## 2. Desglose y visualización de en qué se gasta el dinero

### 2.1. Tabla maestra de transacciones con filtros

* En la parte inferior (o como sección colapsable) de tu dashboard, incluye una **tabla paginada** donde aparezca cada transacción con columnas mínimas:

  * Fecha
  * Detalle (texto completo)
  * Monto
  * Tipo de movimiento (Ingreso/Gasto)
  * Categoría asignada
  * Tipo de regla (ver el punto anterior)
* Incorpora filtros dinámicos en la cabecera de esa tabla:

  * **Filtro por fecha** (desde/hasta o selector de mes/año).
  * **Filtro por categoría** (lista desplegable con todas las categorías, incluyendo “Sin categorizar”).
  * **Filtro por estado** (solo “Ingreso” o solo “Gasto”).
* Asegúrate de que puedas ordenar la tabla por monto (ascendente/descendente) o por fecha. Esto te permitirá, por ejemplo, detectar rápidamente los gastos más altos del mes y ver su detalle y su categoría.

### 2.2. Gráficos de desglose por categoría

* **Gráfico de barras horizontales** (o verticales) que muestre el **total gastado por cada categoría** en el período seleccionado.

  * Ejemplo:

    ```
    Gasto – Alimentos     | ███████████  $1 200 000  
    Gasto – Transporte    | ███████      $750 000  
    Gasto – Servicios     | ███          $350 000  
    …  
    ```
* **Gráfico de pastel o dona** con la proporción de cada categoría sobre el gasto total de ese mes (o rango).
* Si quieres mayor detalle, añade un **heatmap calendario** donde cada día tenga un cuadrado cuyo color represente el monto total gastado ese día; al hacer hover aparecen las categorías más frecuentes de ese día.

### 2.3. Comparación ingreso vs. gasto por categoría

* Actualmente tu dashboard muestra “Ingresos vs Gastos” globales. Agrega un segundo gráfico que cruce **categoría vs. tipo de movimiento**:

  * Por ejemplo, una tabla con dos columnas por categoría:

    ```
    Categoría                   Ingresos  Gastos  
    ------------------------------------------------  
    Ingreso – Sueldos          | $2 500 000  $0  
    Ingreso – Transferencias   | $  800 000  $0  
    Gasto – Alimentos          | $        0  $1 200 000  
    Gasto – Transporte         | $        0  $  750 000  
    Gasto – Servicios          | $        0  $  350 000  
    Sin categorizar            | $  300 000  $  500 000  
    …  
    ```
* De ese modo, no solo ves “pierdo \$X en Alimentos”, sino también “¿hubo ingresos catalogados como Gasto – Alimentos?”.

---

## 3. Capacidad de actualización manual de categorías (“etiquetado interactivo”)

Para que el usuario (tú) pueda corregir una categoría que quedó mal, necesitaremos:

### 3.1. Interfaz de edición directa en la tabla

* En la columna “Categoría” de la tabla de transacciones, cambia la celda estática por:

  * Un elemento `<select>` desplegable (o un menú tipo “typeahead”) que muestre **todas las categorías posibles** (incluyendo “Sin categorizar”).
  * El valor seleccionado inicialmente será la categoría actual.
  * Si haces clic, podrás elegir otra categoría de la lista y, al confirmar (por ejemplo, con un botón “✔” o saliendo del select), esa fila se marca como “pendiente de actualizar”.

### 3.2. Endpoint para actualizar una sola transacción

* En tu backend FastAPI (o la API que uses), define un nuevo endpoint, por ejemplo:

  ```
  PATCH /transacciones/{id}/categoria
  Body JSON: { "nueva_categoria": "Gasto – Alimentos" }
  ```

  * Aquí `id` puede ser:

    * El índice del DataFrame (si cargas todo en memoria).
    * Un identificador único de la transacción (puede ser el campo “Id Transacción” de tu cartola).
  * Al recibir la petición:

    1. Busca la transacción por su `id_transaccion`.
    2. Actualiza el campo `categoria = nueva_categoria`.
    3. Si tienes persistencia en base de datos (SQLite o similar), graba ese cambio permanente. Si no, al menos entrégalo en memoria y devuélvelo en la siguiente recarga.
    4. Devuelve un JSON con `{ "ok": true }` o bien un error si la transacción no existe.

### 3.3. Sincronizar cambios en el frontend

* Cuando el usuario cambie el valor del select en la columna “Categoría”, dispara un `fetch` a ese endpoint `PATCH`.

  * Hasta que la respuesta no regrese “ok”, muestra un spinner o deshabilita esa celda.
  * Si todo sale bien, actualiza en la vista la nueva categoría y, si habías coloreado fila según “tipo\_regla” (p. ej. verde para automático, azul para manual), cambia esa fila a “sobrescritura\_manual” y pinta la etiqueta como tal (tal vez con un ícono de lápiz).
  * Si hay error (por ejemplo, “transacción no encontrada”), marca la fila en rojo y muestra un tooltip con el mensaje de error.

### 3.4. Recalcular totales y gráficos “en vivo”

* Después de un cambio de categoría, los agregados generales (Ingresos totales, Gastos totales, Balance, Transacciones) y los gráficos de “Distribución por Categorías” deben **refrescarse automáticamente** para reflejar el dato corregido.

  * Por ejemplo, si una transacción por \$50 000 estaba en “Gasto – Financiero” pero tú la pasas a “Gasto – Alimentos”, el gráfico de barras horizontales y el pastel deben restar \$50 000 de “Financiero” y sumarlos a “Alimentos”.
  * Para lograrlo, una vez que el `PATCH` regresa éxito, en el frontend vuelve a llamar al endpoint que retorna los resúmenes por categoría (o bien modifica localmente el objeto JavaScript que tienes en memoria).

---

## 4. Identificar y corregir “Sin categorizar”

Muchos movimientos caerán inicialmente en “Sin categorizar”. Para que puedas revisarlos de manera masiva:

### 4.1. Vista filtrada de “Sin categorizar”

* En la tabla principal (o como un “vista alterna”), agrega un botón o pestaña que filtre **solo** las transacciones cuya `categoria == "Sin categorizar"`.
* Esto te permite recorrer de un vistazo todos los movimientos sin categoría y asignarles de uno en uno la categoría correcta (sin necesidad de recorrer 1 000 filas de golpe).

### 4.2. Panel de sugerencias para nuevos mapeos

* Por cada “Sin categorizar”, muestra una sugerencia basada en la **coincidencia parcial** con palabras clave cercanas.

  * Por ejemplo, si el detalle dice “ABONO IP-12345678”, el sistema podría sugerir “¿Quieres asignar ‘Ingreso – Abonos’?” (porque “ABONO” coincide parcialmente con la clave “ABONO” en tu diccionario).
  * O si dice “NETFLIX.COM”, sugerir “Entretenimiento”.
* Esa sugerencia se basa en un pequeño algoritmo de “coincidencia de palabra raíz” (por ejemplo, buscar si dentro de “NETFLIX.COM” existe la subcadena “NETFLIX”).
* Si aceptas la sugerencia, automáticamente cambia la categoría y guarda la nueva regla en memoria (opcionalmente, podrías “aprender” esa asociación y añadirla al diccionario, aunque eso implica un paso extra de validación).

---

## 5. Mejoras en la experiencia de usuario

### 5.1. Resaltar discrepancias y posibles errores

* Agrega una regla adicional que marque en rojo o amarillo las transacciones **inusuales**. Por ejemplo:

  * Si existe un cargo de \$1 000 000 en “Gasto – Alimentos” pero tu promedio histórico en esa categoría es \$200 000, márcalo como “posible outlier”.
  * Si un ingreso de “SUELDO” usualmente cae el día 30 de cada mes, pero este mes cayó día 10, también puedes marcarlo para revisión.
* Estas alertas ayudan a detectar transacciones que tal vez se hayan clasificado mal o que requieran tu atención.

### 5.2. Búsqueda rápida en la tabla

* Añade un campo de búsqueda en la parte superior de la tabla de transacciones que permita filtrar por **cualquier texto** en las columnas `detalle` o `categoría`.

  * Por ejemplo, escribes “NETFLIX” y te muestra solo las filas cuyo `detalle` o `categoría` contengan “NETFLIX”.

### 5.3. Guardar filtros predefinidos

* Permite guardar “vistas” personalizadas:

  1. “Gastos abril 2025”
  2. “Ingresos por transferencias”
  3. “Todas las filas sin categorizar”
* Estas vistas se guardan en el navegador (o en tu base de datos) y puedes seleccionarlas con un clic para aplicar los mismos filtros y ordenamientos en cualquier momento.

---

## 6. Ajustes en el backend para soportar las nuevas funcionalidades

Para que todo lo anterior funcione de forma robusta y escalable, necesitarás cambios menores en tu backend:

### 6.1. Estructura de datos persistentes

* Si no lo has hecho aún, **crea una tabla (o colección) en tu base de datos** que contenga:

  * `id_transaccion` (clave primaria, único para cada línea).
  * `fecha`
  * `detalle`
  * `monto`
  * `tipo_movimiento`
  * `categoria`
  * `tipo_regla` (cadena que indica “mapeo\_por\_palabra\_clave” o “sobrescritura\_manual”).
  * `fecha_modificacion` (timestamp de la última vez que se editó la fila).
* Al cargar inicialmente tus cartolas, importa todas las filas con `tipo_regla="mapeo_por_palabra_clave"` u `"sin_coincidencias"`, según corresponda.
* Cuando alguien edite desde el dashboard, tu endpoint `PATCH /transacciones/{id}/categoria` actualizará:

  * `categoria = nueva_categoria`
  * `tipo_regla = "sobrescritura_manual"`
  * `fecha_modificacion = ahora`

### 6.2. Endpoints adicionales

1. **GET /transacciones/**

   * Debe permitir recibir parámetros opcionales de filtro:

     * `fecha_desde`, `fecha_hasta`
     * `categoria`
     * `tipo_movimiento` (“Ingreso” / “Gasto”)
     * `texto_busqueda` (busca en `detalle`)
   * Devuelve un JSON con la lista paginada de transacciones (incluyendo `categoria` y `tipo_regla`).

2. **GET /resumen/categorias/**

   * Recibe parámetros opcionales: `fecha_desde`, `fecha_hasta`.
   * Agrupa por `categoria` (y opcionalmente por `tipo_movimiento`) y devuelve `{ categoria, total_ingresos, total_gastos }` para cada categoría.
   * Úsalo en el frontend para poblar tanto:

     * El gráfico de barras horizontales de “Gasto por categoría”.
     * El pastel (“dona”) de “Distribución por categorías”.

3. **PATCH /transacciones/{id}/categoria**

   * Recibe `{ nueva_categoria: string }`.
   * Busca la transacción por su `id_transaccion` (o por PK).
   * Actualiza `categoria`, cambia `tipo_regla = "sobrescritura_manual"`, graba `fecha_modificacion = ahora`.
   * Devuelve el registro actualizado en JSON (para que el frontend refresque esa fila sin tener que volver a pedir todo el listado).

---

## 7. Resumen paso a paso de implementación

1. **Backend**

   * Asegúrate de que tu tabla de transacciones incluya los campos `categoria` y `tipo_regla`.
   * Al importar las cartolas, asigna `tipo_regla="mapeo_por_palabra_clave"` o `"sin_coincidencias"`.
   * Implementa:

     * `GET /transacciones` con filtros y paginación.
     * `GET /resumen/categorias` que devuelva totales por categoría.
     * `PATCH /transacciones/{id}/categoria` para actualizar la categoría y marcar `tipo_regla="sobrescritura_manual"`.

2. **Frontend (Astro + React)**

   * **Sección “Cómo funcionan las categorías”**

     * Un modal o acordeón donde, con un simple JSON, muestres tu diccionario de palabras clave → categoría.
   * **Tabla de transacciones**

     * Columnas: Fecha, Detalle, Monto, Tipo de movimiento, Categoría (editable), Tipo de regla (ícono/tooltip).
     * Filtros:

       * Selector de rango de fechas.
       * Desplegable de categorías.
       * Selector “Ingreso/Gasto”.
       * Búsqueda por texto.
     * Paginación o scroll infinito.
     * En la columna “Categoría”:

       * Visualización actual con un `<select>` o “typeahead” al hacer clic.
       * Al cambiar, dispara el `PATCH` que actualiza en el backend.
       * Mientras actualiza, muestra un spinner en esa celda.
       * Si hay error, pinta la celda/fila en rojo y muestra tooltip.
       * Si es éxito, cambia el `tipo_regla` al nuevo valor (“sobrescritura\_manual”) y muestra un ícono de lápiz o etiqueta azul.
   * **Resumen por categorías**

     * Gráfico de barras horizontales y gráfico de dona.
     * Al hacer clic en una barra o en un pedazo de dona, filtra automáticamente la tabla de transacciones para mostrar solo esa categoría.
     * Muestra, junto al gráfico, una pequeña leyenda con:

       * “Total ingresos en X categoría: \$…”
       * “Total gastos en X categoría: \$…”
       * “% del gasto total”
   * **Vista “Sin categorizar”**

     * Un botón o pestaña fija que muestre exclusivamente `df_categorizado[categoria == "Sin categorizar"]`.
     * Dentro de esa vista, agrega un pequeño “sugeridor” que intente igualar alguna palabra de “detalle” a tu diccionario (por ejemplo, si el detalle contiene “NETFLIX”, sugiere “Gasto – Entretenimiento”). Al aceptar, cambia la categoría y se va automáticamente de “Sin categorizar”.

3. **Experiencia adicional**

   * Cada cierto tiempo (por ejemplo, al abrir el dashboard o después de una edición), recalcula los **indicadores globales** de Ingresos, Gastos, Balance y Cantidad de Transacciones.
   * Cuando cambies una categoría, los totales globales y los gráficos deben reflejar el nuevo estado sin recargar toda la página (basta con volver a pedir el endpoint de “resumen por categorías” y “totales generales”).
   * Incorpora pequeños **tooltips** en los títulos de cada gráfica (“Este gráfico muestra la distribución de gastos por categoría en el mes seleccionado”), para que cualquier usuario entienda qué está viendo.

---

## 8. Beneficios de este enfoque

* **Transparencia**: sabrás siempre por qué una transacción aparece en cierto “Gasto – Servicios” (fue porque contuvo la palabra “LAVANDERÍA”, por ejemplo).
* **Control manual**: cualquier error en la categorización automática puede corregirse desde la misma interfaz, y se guardará la corrección para que no se repita.
* **Mejor análisis**: con vistas dinámicas, podrás responder preguntas como:

  * “¿Cuánto gasté en ‘Entretenimiento’ el último trimestre?”
  * “¿Qué gastos no están categorizados que podrían sumar un monto relevante?”
  * “¿Hay ingresos etiquetados en categorías de gasto?” (y corregirlo).
* **Aprendizaje continuo**: al revisar las filas “Sin categorizar” y confirmar sugerencias manuales, tu diccionario de palabras clave se irá perfeccionando, reduciendo el trabajo de corrección futuro.

---

Con estos pasos habrás transformado tu dashboard en una herramienta interactiva, donde no solo obtienes cifras agregadas, sino que comprendes la lógica de categorización y tienes la flexibilidad de ajustarla en tiempo real. Así sabrás exactamente en qué se está yendo tu dinero y podrás perfeccionar continuamente las reglas para que el modelo de categorización te ahorre cada vez más trabajo manual. ¡Éxito implementando estas mejoras!

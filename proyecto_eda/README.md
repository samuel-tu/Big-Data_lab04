# Laboratorio 04 – Análisis Exploratorio de Datos con Python

## 1. Descripción del proyecto

Este proyecto corresponde al Laboratorio 04 de la asignatura Big Data y tiene como objetivo desarrollar un proceso reproducible de análisis exploratorio de datos (EDA) utilizando Python.

El análisis se realiza sobre un conjunto de estadísticas criminales de la India, provenientes de datos del National Crime Records Bureau (NCRB), organizados por estado, año, categoría del delito y tipo de medición.

El proyecto contempla la carga e inspección de datos, diagnóstico de calidad, limpieza y preparación, estadística descriptiva, relaciones entre variables y generación de visualizaciones.

## 2. Dataset utilizado

- **Nombre:** India Crime Data: NCRB Statistics & News (CrimeBase).
- **Archivo:** `crime_state_year.zip`, que contiene `crime_state_year.csv`.
- **Autor del dataset:** Chandransh Binjola.
- **Fuente original de estadísticas:** National Crime Records Bureau (NCRB), India.
- **Repositorio:** https://www.kaggle.com/datasets/chandranshbinjola/crimebase/data
- **Fecha de descarga:** 20/10/2026.
- **Cantidad de registros:** 668.240.
- **Cantidad de columnas:** 12.
- **Periodo:** 2001–2022.

El conjunto de datos conserva las observaciones originales después de la preparación, dado que no se identificaron duplicados exactos ni errores que justificaran eliminar registros automáticamente.

El archivo comprimido se encuentra en `datos/crime_state_year.zip`. Se utiliza la copia incluida en el proyecto para garantizar que los análisis sean reproducibles con la misma versión de los datos.

**Condiciones de uso:** la publicación en Kaggle indica condiciones especificadas en la descripción. Los datos estadísticos provienen de fuentes oficiales y sus condiciones de reutilización deben consultarse en la fuente correspondiente. El autor del proyecto CrimeBase solicita citar su trabajo.

El diccionario de variables se encuentra en `datos/DATA_DICTIONARY.md`.

## 3. Estructura del proyecto

```text
proyecto_eda/
├── analisis_exploratorio.py
├── visualizaciones.py
├── requirements.txt
├── README.md
├── datos/
│   ├── crime_state_year.zip
│   └── DATA_DICTIONARY.md
└── resultados/
    ├── tablas/
    └── figuras/
```

**Descripción de los archivos principales:**

- `analisis_exploratorio.py`: script principal que ejecuta las etapas del análisis.
- `visualizaciones.py`: funciones para generar gráficos estadísticos.
- `requirements.txt`: dependencias de Python utilizadas.
- `README.md`: documentación para instalar y ejecutar el proyecto.
- `DATA_DICTIONARY.md`: descripción de las variables del dataset.
- `resultados/tablas/`: archivos CSV con diagnósticos y estadísticas.
- `resultados/figuras/`: gráficos generados en formato PNG.

## 4. Requisitos del sistema

Se requiere Python 3 y las siguientes bibliotecas, con las versiones utilizadas en el entorno de ejecución verificado:

| Biblioteca | Versión |
|---|---|
| pandas | 2.2.3 |
| NumPy | 1.26.4 |
| Matplotlib | 3.11.2 |
| Seaborn | 0.13.2 |

**Versión exacta de Python:** 3.11.13.

Se recomienda utilizar un entorno virtual para aislar las dependencias del proyecto.

## 5. Instalación y ejecución

### 5.1. Obtener el proyecto

Clonar el repositorio del equipo desde GitHub o descargarlo mediante la opción **Code → Download ZIP**.

Luego, abrir una terminal dentro de la carpeta `proyecto_eda`.

### 5.2. Crear un entorno virtual (opcional, recomendado)

```powershell
python -m venv .venv
```

Activar el entorno virtual en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5.3. Instalar las dependencias

```powershell
python -m pip install -r requirements.txt
```

### 5.4. Ejecutar el análisis

```powershell
python analisis_exploratorio.py
```

El script utiliza rutas relativas, por lo que debe ejecutarse desde la carpeta `proyecto_eda`.

**No es necesario descomprimir manualmente el dataset.** El programa lee `crime_state_year.zip` mediante pandas.

## 6. Etapas del análisis

### 6.1. Carga e inspección

La función `cargar_e_inspeccionar_datos()` lee el archivo de entrada, revisa dimensiones y tipos, muestra observaciones iniciales y valida el mínimo de 50.000 registros.

### 6.2. Diagnóstico de calidad

La función `diagnostico_calidad()` permite detectar valores faltantes, duplicados exactos y repeticiones según una combinación de columnas.

### 6.3. Limpieza y preparación

La función `limpiar_y_preparar_datos()` realiza validaciones de tipos, años y valores negativos, identifica posibles valores atípicos mediante IQR y revisa observaciones decimales.

Las decisiones de conservación y las cantidades antes y después de cada etapa se documentan en un registro de limpieza.

### 6.4. Estadística descriptiva

La función `estadistica_descriptiva()` calcula:

- Cantidad de observaciones válidas.
- Media y mediana.
- Desviación estándar.
- Mínimo, máximo y cuartiles.
- Frecuencias y porcentajes categóricos.
- Comparaciones entre estados.

Las estadísticas numéricas se agrupan por tipo de métrica para evitar mezclar cantidades de distinta naturaleza.

### 6.5. Relaciones entre variables

Se analizan las relaciones entre casos registrados y personas detenidas, utilizando correlaciones de Pearson y Spearman. También se calculan medidas derivadas como detenidos por caso y proporciones de condenas.

Las asociaciones identificadas no deben interpretarse como relaciones causales.

### 6.6. Visualización

Se generan seis figuras:

1. Distribución de casos registrados.
2. Valores extremos y evolución temporal.
3. Dispersión entre casos y detenidos.
4. Comparación de estados con mayor cantidad acumulada de casos.
5. Matriz de correlación.
6. Comparación del crecimiento por categorías de delitos.

## 7. Resultados generados

Los resultados se exportan automáticamente a las carpetas correspondientes.

### Tablas CSV

Entre los archivos generados se encuentran:

- `diagnostico_nulos.csv`
- `resumen_diagnostico.csv`
- `registro_limpieza_detallado.csv`
- `revision_decimales.csv`
- `estadisticas_numericas.csv`
- `frecuencias_categoricas.csv`
- `comparacion_estados.csv`
- `correlacion_casos_detenidos.csv`
- `pares_casos_detenidos.csv`
- `detenidos_por_caso_estado.csv`
- `comparacion_condenas_scope.csv`

### Figuras PNG

- `figura1_distribucion.png`
- `figura2_valores_extremos.png`
- `figura3_dispersion.png`
- `figura4_top_estados.png`
- `figura5_matriz_correlacion.png`
- `figura6_pregunta_crecimiento.png`

Las carpetas de salida se crean automáticamente cuando corresponde y sus resultados pueden regenerarse ejecutando el script.

## 8. Decisiones de limpieza y limitaciones

El proceso conserva los 668.240 registros y las 12 columnas originales.

Entre los hallazgos de calidad se identificaron:

- 499.260 valores faltantes en `table_id`, conservados por tratarse de un identificador documental opcional.
- Cero duplicados exactos.
- Cero valores negativos y ningún año fuera del periodo documentado.
- 141 observaciones decimales en `cases_registered`, conservadas para revisión.
- Valores potencialmente atípicos mediante IQR, conservados al no existir evidencia suficiente para clasificarlos automáticamente como errores.

Las comparaciones pueden verse afectadas por diferencias de población, cobertura temporal, clasificaciones de delitos y prácticas de registro.

Los datos representan estadísticas criminales registradas, no necesariamente todos los delitos ocurridos. No incluyen las poblaciones necesarias para calcular tasas de criminalidad por habitante.

## 9. Reproducibilidad

Para reproducir los resultados:

1. Obtener el proyecto con el archivo original `crime_state_year.zip`.
2. Instalar las dependencias indicadas en `requirements.txt`.
3. Ejecutar `python analisis_exploratorio.py` desde `proyecto_eda`.
4. Consultar los resultados generados en `resultados/tablas/` y `resultados/figuras/`.

El dataset procesado se obtiene en memoria mediante la función limpiar_y_preparar_datos(), a partir del archivo original comprimido.
Se conservan las 668.240 observaciones y las 12 columnas, sin eliminación de registros. El proceso completo puede reproducirse ejecutando analisis_exploratorio.py, y los resultados del análisis se exportan automáticamente a las carpetas correspondientes.

Los análisis principales utilizan el conjunto completo de datos y no requieren muestreo aleatorio.

## 10. Integrantes y responsabilidades

| Integrante | Responsabilidad |
|---|---|
| Javiera Fuentealba | Carga, inspección y diagnóstico de calidad |
| Samuel López | Limpieza, preparación y estadística descriptiva |
| José Arguello | Relaciones entre variables |
| Patricio Chaug | Visualizaciones |

El desarrollo del proyecto se realizó colaborativamente mediante Git y GitHub, permitiendo mantener un historial de contribuciones por integrante.

## 11. Referencias

- Chandransh Binjola. *CrimeBase: India Crime Data*. Kaggle. https://www.kaggle.com/datasets/chandranshbinjola/crimebase/data
- National Crime Records Bureau (NCRB). *Crime in India*, informes estadísticos del periodo 2001–2022. Gobierno de la India.


import os
import sys
import logging
import pandas as pd
import numpy as np
from pathlib import Path

# Configuración de registro de eventos (logging)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------------------------------------------------------------
# RUTAS RELATIVAS Y CONFIGURACIÓN DEL PROYECTO
# -----------------------------------------------------------------------------
RUTA_DATOS = os.path.join("datos", "crime_state_year.csv")
DIR_TABLAS = os.path.join("resultados", "tablas")
DIR_FIGURAS = os.path.join("resultados", "figuras")


# -----------------------------------------------------------------------------
# 1. CARGA E INSPECCIÓN
# -----------------------------------------------------------------------------
def cargar_e_inspeccionar_datos(ruta_archivo, separador=',', codificacion='utf-8'):
    """
    Carga el dataset desde una ruta relativa configurable, valida el tamaño mínimo
    (>= 50.000 registros) e inspecciona dimensiones, tipos de datos y primeras filas.
    """
    logging.info(f"Cargando dataset desde: {ruta_archivo}")
    
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(
            f"No se encontró el archivo en: {ruta_archivo}. "
            f"Asegúrate de haber copiado 'crime_state_year.csv' dentro de la carpeta 'datos/'."
        )

    try:
        df = pd.read_csv(ruta_archivo, sep=separador, encoding=codificacion, low_memory=False)
    except UnicodeDecodeError:
        logging.warning("Error de codificación con UTF-8. Intentando con 'latin-1'...")
        df = pd.read_csv(ruta_archivo, sep=separador, encoding='latin-1', low_memory=False)
    except Exception as e:
        raise RuntimeError(f"Error crítico al leer el archivo CSV: {e}")

    filas, columnas = df.shape
    logging.info(f"Dimensiones de entrada: {filas:,} filas x {columnas} columnas.")

    # Validación del requisito de al menos 50.000 registros
    if filas < 50000:
        raise ValueError(
            f"El dataset NO cumple con el mínimo de 50.000 registros. "
            f"Registros encontrados: {filas:,}"
        )
    
    logging.info("VALIDACIÓN EXITOSA: El dataset cumple con el mínimo de 50.000 registros de entrada.")

    # Resumen de estructura
    resumen_columnas = pd.DataFrame({
        "Columna": df.columns,
        "Tipo_Dato": df.dtypes.astype(str),
        "Primeros_Valores": [df[col].dropna().head(2).tolist() for col in df.columns]
    })

    print("\n" + "="*70)
    print(" RESUMEN DE ESTRUCTURA Y TIPOS DE DATOS ")
    print("="*70)
    print(resumen_columnas.to_string(index=False))

    return df


# -----------------------------------------------------------------------------
# 2. DIAGNÓSTICO DE CALIDAD DE DATOS
# -----------------------------------------------------------------------------
def diagnostico_calidad(df, columnas_entidad=None, rangos_plausibles=None, ruta_salida_tablas=DIR_TABLAS):
    """
    Cuantifica valores faltantes, duplicados exactos, repeticiones de entidad
    y valores fuera de rango. Exporta tablas de diagnóstico a resultados/tablas/.
    """
    os.makedirs(ruta_salida_tablas, exist_ok=True)
    logging.info("Ejecutando diagnóstico de calidad...")

    # A. Valores Faltantes por Columna
    nulos_por_col = df.isnull().sum()
    pct_nulos = (nulos_por_col / len(df)) * 100
    reporte_nulos = pd.DataFrame({
        "Columna": df.columns,
        "Valores_Faltantes": nulos_por_col,
        "Porcentaje_%": pct_nulos.round(2)
    }).sort_values(by="Valores_Faltantes", ascending=False)

    print("\n" + "="*70)
    print(" REPORTE DE VALORES FALTANTES POR COLUMNA ")
    print("="*70)
    print(reporte_nulos.to_string(index=False))

    # B. Duplicados Exactos vs Entitativos
    duplicados_exactos = int(df.duplicated().sum())
    logging.info(f"Duplicados exactos detectados: {duplicados_exactos}")

    duplicados_entidad = 0
    if columnas_entidad:
        duplicados_entidad = int(df.duplicated(subset=columnas_entidad).sum())
        logging.info(
            f"Repeticiones de entidad ({columnas_entidad}): {duplicados_entidad} "
            f"(Plausibles si representan múltiples registros por entidad/año)."
        )

    # C. Revisión de Valores Fuera de Rangos Plausibles
    reporte_rangos = []
    if rangos_plausibles:
        for col, (min_val, max_val) in rangos_plausibles.items():
            if col in df.columns and np.issubdtype(df[col].dtype, np.number):
                fuera_de_rango = int(df[(df[col] < min_val) | (df[col] > max_val)][col].count())
                reporte_rangos.append({
                    "Columna": col,
                    "Rango_Esperado": f"[{min_val}, {max_val}]",
                    "Valores_Fuera_Rango": fuera_de_rango,
                    "Porcentaje_%": round((fuera_de_rango / len(df)) * 100, 2)
                })

    reporte_rangos_df = pd.DataFrame(reporte_rangos)
    if not reporte_rangos_df.empty:
        print("\n" + "="*70)
        print(" REPORTE DE VALORES FUERA DE RANGO ")
        print("="*70)
        print(reporte_rangos_df.to_string(index=False))

    # Exportación de diagnósticos a CSV
    reporte_nulos.to_csv(os.path.join(ruta_salida_tablas, "diagnostico_nulos.csv"), index=False)
    
    resumen_diagnostico = pd.DataFrame([{
        "Total_Registros_Entrada": len(df),
        "Duplicados_Exactos": duplicados_exactos,
        "Repeticiones_Entidad": duplicados_entidad,
        "Columnas_Con_Nulos": int((nulos_por_col > 0).sum())
    }])
    resumen_diagnostico.to_csv(os.path.join(ruta_salida_tablas, "resumen_diagnostico.csv"), index=False)

    logging.info(f"Tablas de diagnóstico exportadas correctamente en '{ruta_salida_tablas}/'.")
    return reporte_nulos, resumen_diagnostico


#3. Limpieza y preparacion de datos
def limpiar_y_preparar_datos(df, ruta_salida_tablas=DIR_TABLAS):
    """
    limpia y prepara el dataset a partir del diagnostico de calidad.
    parametros:
        - df: Dataframe original
        - ruta_salida_tabla: carpeta para guardar el registro de limpieza
    retorna:
        df_limpio: Dataframe procesado
    """
    ruta_salida_tablas = Path(ruta_salida_tablas)
    ruta_salida_tablas.mkdir(parents=True, exist_ok=True)
    logging.info("Iniciando limpieza y preparacion de datos...")
    #hacemos una copia para no modificar los datos originales
    df_limpio=df.copy()
    #registrar las transformaciones realizadas
    registro_limpieza=[]
    #cantidad inicial de registros
    filas_iniciales=len(df_limpio)
    
    logging.info(f"registros iniciales: {filas_iniciales:,}")

    #3.1 Tratamiento de valores faltantes
    filas_antes=len(df_limpio)
    #identificacion de cantidad de valores nulos por columna
    valores_nulos=df_limpio.isnull().sum()
    for columna, cantidad in valores_nulos.items():
        if cantidad > 0:
            logging.warning(
                f"columna '{columna}':{cantidad} valores faltantes."
            )
            #table_id es un identificador documental opcional
            if columna=="table_id":
                decision="conservar valores nulos: identificador opcional"
            else:
                decision="conservar temporalmente para revision"

            registro_limpieza.append({
                "transformacion": f"revision de nulos en {columna}",
                "decision": decision,
                "filas_antes":filas_antes,
                "filas_despues":len(df_limpio)
            })

    logging.info("Revision de valores faltantes finalizada")

    #3.2 Tratamiento de duplicados exactos
    filas_antes=len(df_limpio)
    duplicados_exactos=df_limpio.duplicated().sum()

    if duplicados_exactos > 0:
        logging.warning(
            f"Se encontraron {duplicados_exactos} duplicados exactos"
        )
        df_limpio = df_limpio.drop_duplicates().copy()
        decision="Eliminar filas completamente identicas."
    else:
        logging.info("No se encontraron duplicados exactos")
        decision="conservar registros: no existen duplicados exactos"

    registro_limpieza.append({
        "transformacion": "revision de duplicados exactos",
        "decision": decision,
        "filas_antes":filas_antes,
        "filas_despues":len(df_limpio)
    })

    #3.3 Validacion de tipos
    filas_antes=len(df_limpio)

    for columna in ["year", "value"]:
        #conversion a numerico, los valores invalidos pasan a NaN
        valores_convertidos=pd.to_numeric(
            df_limpio[columna], errors="coerce" #detecta valores que no se pueden convertir a numeros
        )

        conversiones_invalidas=(
            df_limpio[columna].notna() &
            valores_convertidos.isna()
        ).sum()

        if conversiones_invalidas==0:
            df_limpio[columna]=valores_convertidos
            decision="Conversion numerica validad"
        else:
            decision=(
                f"Se detectaron {conversiones_invalidas} valores "
                "no convertibles. Se conservo la columna original."
            )
            logging.warning(decision)

        registro_limpieza.append({
            "transformacion": f"Validacion del tipo de {columna}",
            "decision": decision,
            "filas_antes":filas_antes,
            "filas_despues":len(df_limpio)
        })

    #Verificacion detipo de columna booleana
    if pd.api.types.is_bool_dtype(df_limpio["disputed"]):
        logging.info("Lacolumna disputed tiene tipo booleano valido")
    else:
        logging.warning(
            "La columna disputed requiere revision de tipo"
        )

    #3.4 Validacion de Rangos Plausibles
    filas_antes=len(df_limpio)

    anios_invalidos=(
        df_limpio["year"].notna() & 
        ~df_limpio["year"].between(2001,2022)
    ).sum()

    valores_negativos=(df_limpio["value"]<0).sum()

    logging.info(f"Años fuera del periodo: {anios_invalidos}")
    logging.info(f"Valores negativos: {valores_negativos}")

    #Se conservan registros sospechosos/poco claros, no se modifican ni se eliminan
    registro_limpieza.append({
        "transformacion": "Validacion de rangos.",
        "decision": (
            f"{anios_invalidos} años fuera de periodos y "
            f"{valores_negativos} valores negativos. "
            "Los registros sospechosos se conservan para revision."
        ),
        "filas_antes":filas_antes,
        "filas_despues":len(df_limpio)
    })

    #3.5 Deteccion de valores extremos
    filas_antes=len(df_limpio)

    for metrica, grupo in df_limpio.groupby("metric"):
        q1 = grupo["value"].quantile(0.25)
        q3 = grupo["value"].quantile(0.75)
        iqr = q3 - q1
        limite_inferior = q1 - (1.5 * iqr)
        limite_superior = q3 + (1.5 * iqr)
        
        extremos = grupo[
            (grupo["value"] < limite_inferior) |
            (grupo["value"] > limite_superior)
        ]

        cantidad_extremos=len(extremos)
        logging.info(
            f"Metrica {metrica}: "
            f"{cantidad_extremos} valores potencialmente atipicos"
        )

        registro_limpieza.append({
            "transformacion": f"Revision de extremos: {metrica}",
            "decision": (
                f"{cantidad_extremos} valores fuera del IQR. "
                "Se conservan por no existir evidencia suficiente "
                "para clasificarlos como errore.s"
            ),
            "filas_antes":filas_antes,
            "filas_despues":len(df_limpio)
        })

    #3.6 Revision de Valores decimales
    filas_antes=len(df_limpio)
    #identificacion de valores numericos no enteros
    mascara_decimales=(
        df_limpio["value"].notna() & 
        (df_limpio["value"] % 1 != 0)
    )
    #Obtener solo los regist5ros con valores decimales
    registro_decimales = df_limpio.loc[mascara_decimales].copy()
    cantidad_decimales = len(registro_decimales)
    logging.info(
        f"Se encontraron {cantidad_decimales} valores decimales"
    )
    #Resumir los decimales segun la metrica
    if cantidad_decimales > 0:
        resumen_decimales = (
            registro_decimales.groupby("metric").size().reset_index(name="cantidad")
        )

        logging.info(
            f"Distribucion de decimales:\n"
            f"{resumen_decimales.to_string(index=False)}"
        )

        #Guardar los registros para revision posterior
        registro_decimales.to_csv(
            ruta_salida_tablas / "revision_decimales.csv",
            index=False,
            encoding="utf-8-sig"
        )

        logging.info(
            "Archivo revision_decimales.csv generado correctamente"
        )
    else:
        logging.info(
            "No se encontraron valores decimales"
        )

    #registro de la decision de limpieza
    registro_limpieza.append({
        "transformacion": "Revision de valores decimales",
        "decision": (
            f"{cantidad_decimales} valores decimales detectados. "
            "Se conservan sin redondear porque no existe "
            "evidencia suficiente para clasificarlos como errores."
        ),
        "filas_antes":filas_antes,
        "filas_despues":len(df_limpio)
    })

    #3.7 Exportacion del registro de limpieza
    #Convertir la lista de transformaciones en un DAtaFrame
    df_registro = pd.DataFrame(registro_limpieza)

    #Calcular cuantas filas  fueron eliminadas en cada etapa
    df_registro["filas_eliminadas"] = (
        df_registro["filas_antes"] - 
        df_registro["filas_despues"]
    )

    #Definir la ruta del archivo de salida
    ruta_registro= ruta_salida_tablas / "registro_limpieza_detallado.csv"

    #Exportar el registro a un archivo CSV
    df_registro.to_csv(
        ruta_registro,
        index=False,
        encoding="utf-8-sig"
    )

    logging.info(
        f"Registro de limpieza guardado en: {ruta_registro}"
    )

    #Informar del resultado final de la limpieza
    logging.info(
        f"Limpieza finalizada."
        f"Registros iniciales: {filas_iniciales:,} |"
        f"Registros finales: {len(df_limpio):,}"
    )

    return df_limpio

# 4. ESTADÍSTICA DESCRIPTIVA
def estadistica_descriptiva(df, ruta_salida_tablas=DIR_TABLAS):
    """
    Calcula estadísticas descriptivas de las variables numéricas,
    separando los resultados según el tipo de métrica.
    """

    logging.info("Iniciando estadística descriptiva...")

    # Crear la carpeta de resultados si no existe.
    ruta_salida_tablas = Path(ruta_salida_tablas)
    ruta_salida_tablas.mkdir(parents=True, exist_ok=True)

    # 4.1 Estadísticas descriptivas de la variable value
    resumen_numerico = (
        df.groupby("metric")["value"]
        .agg(
            cantidad_validos="count",
            media="mean",
            mediana="median",
            desviacion_estandar="std",
            minimo="min",
            maximo="max",
            q1=lambda x: x.quantile(0.25),
            q3=lambda x: x.quantile(0.75)
        )
        .reset_index()
    )

    # Redondear resultados para facilitar su lectura.
    columnas_numericas = resumen_numerico.select_dtypes(
        include="number"
    ).columns.difference(["cantidad_validos"])

    resumen_numerico[columnas_numericas] = (
        resumen_numerico[columnas_numericas].round(2)
    )

    # Mostrar resultados en terminal.
    print("\n" + "=" * 70)
    print(" ESTADÍSTICAS DESCRIPTIVAS POR MÉTRICA ")
    print("=" * 70)
    print(resumen_numerico.to_string(index=False))

    # Exportar resultados.
    resumen_numerico.to_csv(
        ruta_salida_tablas / "estadisticas_numericas.csv",
        index=False,
        encoding="utf-8-sig"
    )

    logging.info("Estadísticas numéricas exportadas correctamente.")

    
    # 4.2 Frecuencias y porcentajes de variables categóricas
    # Seleccionar las columnas categóricas relevantes
    columnas_categoricas = [
        "state",
        "scope",
        "crime_category",
        "metric",
        "source"
    ]

    # Lista para almacenar las tablas de frecuencias
    tablas_frecuencias = []

    for columna in columnas_categoricas:

        # Contar cuántas veces aparece cada categoría
        frecuencias = (
            df[columna]
            .value_counts(dropna=False)   #cuenta la cantidad de aparicion por categoria y dropna=False para incluir valores faltantes
            .rename_axis("categoria")
            .reset_index(name="frecuencia")
        )

        # Calcular el porcentaje de cada categoría
        frecuencias["porcentaje"] = (
            frecuencias["frecuencia"] / len(df) * 100   #calculo de porcentaje que una categoria representa del total de registros
        ).round(2)

        # Identificar la columna analizada
        frecuencias.insert(0, "variable", columna)

        # Almacenar los resultados
        tablas_frecuencias.append(frecuencias)

        logging.info(
            f"Frecuencias calculadas para: {columna}"
        )

    # Unificar las tablas de frecuencias
    resumen_categorico = pd.concat(
        tablas_frecuencias,
        ignore_index=True
    )

    # Exportar las frecuencias y porcentajes
    resumen_categorico.to_csv(
        ruta_salida_tablas / "frecuencias_categoricas.csv",
        index=False,
        encoding="utf-8-sig"
    )

    logging.info(
        "Frecuencias categóricas exportadas correctamente."
    )

    
    # 4.3 Comparación estadística entre estados
    # Seleccionar registros comparables
    df_comparacion = df[
        (df["metric"] == "cases_registered") &
        (df["source"] == "state_table") &
        (df["scope"] == "ipc")
    ].copy()

    # Calcular estadísticas agrupadas por estado
    comparacion_estados = (
        df_comparacion
        .groupby("state")["value"]
        .agg(
            cantidad_registros="count",
            media="mean",
            mediana="median",
            minimo="min",
            maximo="max"
        )
        .reset_index()
    )

    # Ordenar los estados según su mediana
    comparacion_estados = comparacion_estados.sort_values(
        by="mediana",
        ascending=False
    )

    # Redondear los resultados
    columnas_redondear = [
        "media", "mediana", "minimo", "maximo"
    ]

    comparacion_estados[columnas_redondear] = (
        comparacion_estados[columnas_redondear].round(2)
    )

    # Mostrar los primeros 10 estados
    print("\n" + "=" * 70)
    print(" COMPARACIÓN ESTADÍSTICA ENTRE ESTADOS ")
    print("=" * 70)
    print(comparacion_estados.head(10).to_string(index=False))

    # Exportar la comparación completa
    comparacion_estados.to_csv(
        ruta_salida_tablas / "comparacion_estados.csv",
        index=False,
        encoding="utf-8-sig"
    )

    logging.info(
        "Comparación estadística entre estados exportada."
    )


    return resumen_numerico

# 5. RELACIONES ENTRE VARIABLES
def relaciones_entre_variables(df, ruta_salida_tablas=DIR_TABLAS):
    """
    Explora la relacion entre casos registrados y personas detenidas,
    y compara la proporcion de condenas entre familias de delitos.
    """
    ruta_salida_tablas = Path(ruta_salida_tablas)
    ruta_salida_tablas.mkdir(parents=True, exist_ok=True)
    logging.info("Iniciando analisis de relaciones entre variables...")

    #5.1 total de delitos IPC por estado y año, una columna por metrica
    totales_ipc = df[
        (df["scope"] == "ipc") &
        (df["crime_head"].isin(["Total Cognizable IPC Crimes", "TOTAL IPC CRIMES"]))
    ]
    tabla = totales_ipc.pivot_table(
        index=["state", "year"], columns="metric", values="value"
    ).reset_index()

    #solo los estado-año que tienen las dos variables
    pares = tabla.dropna(subset=["cases_registered", "persons_arrested"]).copy()
    logging.info(f"Pares estado-año para la relacion: {len(pares)}")

    #5.2 correlacion entre casos registrados y personas detenidas
    pearson = pares["cases_registered"].corr(pares["persons_arrested"])
    #spearman = pearson calculado sobre los rangos de cada variable
    spearman = pares["cases_registered"].rank().corr(pares["persons_arrested"].rank())

    tabla_correlacion = pd.DataFrame([
        {"variables": "cases_registered vs persons_arrested", "metodo": "pearson",
         "coeficiente": round(pearson, 4), "pares": len(pares)},
        {"variables": "cases_registered vs persons_arrested", "metodo": "spearman",
         "coeficiente": round(spearman, 4), "pares": len(pares)}
    ])
    print("\n" + "=" * 70)
    print(" CORRELACION ENTRE VARIABLES ")
    print("=" * 70)
    print(tabla_correlacion.to_string(index=False))

    #5.3 personas detenidas por cada caso registrado (quita el efecto del tamaño del estado)
    pares = pares[pares["cases_registered"] > 0].copy()
    pares["detenidos_por_caso"] = pares["persons_arrested"] / pares["cases_registered"]

    detenidos_estado = (
        pares.groupby("state")["detenidos_por_caso"]
        .agg(anios="count", mediana="median", minimo="min", maximo="max")
        .reset_index()
        .sort_values(by="mediana", ascending=False)
    )

    #5.4 proporcion de condenas por familia de delitos (scope)
    totales = df[df["crime_category"] == "all_crimes"]
    condenas = totales.pivot_table(
        index=["state", "year", "scope", "crime_head"], columns="metric", values="value"
    ).reset_index()
    condenas = condenas.dropna(subset=["cases_convicted", "cases_chargesheeted"])
    condenas = condenas[condenas["cases_chargesheeted"] > 0].copy()
    condenas["proporcion_condena"] = condenas["cases_convicted"] / condenas["cases_chargesheeted"]

    comparacion_scope = (
        condenas.groupby("scope")["proporcion_condena"]
        .agg(
            cantidad="count",
            mediana="median",
            q1=lambda x: x.quantile(0.25),
            q3=lambda x: x.quantile(0.75),
            maximo="max"
        )
        .reset_index()
        .sort_values(by="mediana", ascending=False)
        .round(4)
    )
    print("\n" + "=" * 70)
    print(" PROPORCION DE CONDENAS POR SCOPE ")
    print("=" * 70)
    print(comparacion_scope.to_string(index=False))

    #5.5 exportacion
    tabla_correlacion.to_csv(ruta_salida_tablas / "correlacion_casos_detenidos.csv", index=False, encoding="utf-8-sig")
    pares.to_csv(ruta_salida_tablas / "pares_casos_detenidos.csv", index=False, encoding="utf-8-sig")
    detenidos_estado.to_csv(ruta_salida_tablas / "detenidos_por_caso_estado.csv", index=False, encoding="utf-8-sig")
    comparacion_scope.to_csv(ruta_salida_tablas / "comparacion_condenas_scope.csv", index=False, encoding="utf-8-sig")

    logging.info("Tablas de relaciones entre variables exportadas.")
    return tabla_correlacion

# -----------------------------------------------------------------------------
# BLOQUE PRINCIPAL
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        # 1. Carga e Inspección
        df_crimenes = cargar_e_inspeccionar_datos(
            ruta_archivo=RUTA_DATOS,
            separador=',',
            codificacion='utf-8'
        )

        # 2. Diagnóstico de Calidad Inicial
        diagnostico_calidad(
            df=df_crimenes,
            columnas_entidad=None,
            rangos_plausibles=None
        )

        # 3. Limpieza y preparacion de datos
        df_limpio = limpiar_y_preparar_datos(
            df=df_crimenes,
            ruta_salida_tablas=DIR_TABLAS
        )
        logging.info(
            f"Dataset procesado: {df_limpio.shape[0]:,} filas"
            f"y {df_limpio.shape[1]} columnas."
        )

        #4. Estadistica descriptiva
        resumen_estadistico = estadistica_descriptiva(
            df=df_limpio,
            ruta_salida_tablas=DIR_TABLAS
        )

        
        #5. Relaciones entre variables
        relaciones_entre_variables(
            df=df_limpio,
            ruta_salida_tablas=DIR_TABLAS
        )
        #6. Generar Visualizacion (Graficos)
        generar_visualizaciones(
            df=df_limpio,
            ruta_salida_figuras=DIR_FIGURAS
        )

    except Exception as error:
        logging.error(f"Ocurrió un error durante la ejecución: {error}")
        sys.exit(1)

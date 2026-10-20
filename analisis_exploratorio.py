import os
import sys
import logging
import pandas as pd
import numpy as np

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

    except Exception as error:
        logging.error(f"Ocurrió un error durante la ejecución: {error}")
        sys.exit(1)
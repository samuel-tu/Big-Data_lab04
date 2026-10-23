import logging
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

DIR_FIGURAS = os.path.join("resultados", "figuras")
DPI = 300
SCOPE_IPC = "ipc"
TOTALES_IPC = ["Total Cognizable IPC Crimes", "TOTAL IPC CRIMES"]
CATEGORIA_TOTAL = "all_crimes"
ESTILO = "seaborn-v0_8-whitegrid"

ETIQUETAS_METRICAS = {
    "cases_registered": "Casos registrados",
    "cases_chargesheeted": "Casos con cargos",
    "cases_convicted": "Casos con condena",
    "persons_arrested": "Personas detenidas",
    "persons_chargesheeted": "Personas con cargos",
    "persons_convicted": "Personas condenadas",
    "victims": "Víctimas",
}

def _estilo():
    plt.style.use(ESTILO if ESTILO in plt.style.available else "default")

def _formato_miles(valor, _pos):
    return f"{valor:,.0f}"

def _unicos(subconjunto, claves):
    salida = subconjunto.drop_duplicates(subset=claves, keep="first")
    eliminadas = len(subconjunto) - len(salida)
    if eliminadas:
        logging.warning(
            f"{eliminadas} filas con claves repetidas {claves} omitidas solo para graficar."
        )
    return salida
def _total_ipc(df, metrica):
    return df[
        (df["metric"] == metrica)
        & (df["scope"] == SCOPE_IPC)
        & (df["crime_head"].isin(TOTALES_IPC))
    ]
def _guardar(figura, ruta):
    figura.tight_layout()
    figura.savefig(ruta, dpi=DPI)
    plt.close(figura)
    logging.info(f"Figura guardada: {ruta}")

# Figura 1: distribucion
def figura1_distribucion(df, ruta):
    base = df[
        (df["metric"] == "cases_registered")
        & (df["scope"] == SCOPE_IPC)
        & (df["crime_category"] != CATEGORIA_TOTAL)
        & (~df["crime_head"].isin(TOTALES_IPC))
    ]
    base = _unicos(base, ["state", "year", "crime_head"])
    datos = base.loc[base["value"] >= 1, "value"]
    intervalos = np.logspace(0, np.log10(datos.max()), 30)
    _estilo()
    figura, eje = plt.subplots(figsize=(10, 6))
    eje.hist(datos, bins=intervalos, color="#348abd", edgecolor="black", alpha=0.85)
    eje.set_xscale("log")
    eje.xaxis.set_major_formatter(FuncFormatter(_formato_miles))
    eje.set_title(
        "Figura 1. Distribución de casos registrados por delito (IPC)",
        fontsize=12, fontweight="bold",
    )
    eje.set_xlabel("Casos registrados por fila (escala logarítmica)")
    eje.set_ylabel("Número de filas (estado-año-delito)")
    eje.grid(True, linestyle="--", alpha=0.5)
    _guardar(figura, ruta)

# Figura 2: valores extremos
def figura2_valores_extremos(df, ruta):
    base = df[
        (df["metric"] == "cases_registered")
        & (df["scope"] == SCOPE_IPC)
        & (df["crime_head"].isin(TOTALES_IPC))
        & (df["value"] >= 1)
    ]
    base = _unicos(base, ["state", "year"])
    años = sorted(base["year"].unique())
    datos = [base.loc[base["year"] == año, "value"].values for año in años]
    etiquetas = [f"{int(año)}\n(n={len(d)})" for año, d in zip(años, datos)]
    _estilo()
    figura, eje = plt.subplots(figsize=(12, 6.5))
    eje.boxplot(
        datos,
        patch_artist=True,
        showfliers=True,
        flierprops=dict(marker="o", markersize=3, alpha=0.5,
                        markerfacecolor="#d95f02", markeredgecolor="none"),
        boxprops=dict(facecolor="#a6cee3", color="#1f77b4"),
        medianprops=dict(color="#d95f02", linewidth=2.2),
        whiskerprops=dict(color="black"),
        capprops=dict(color="black"),
    )
    eje.set_xticks(range(1, len(años) + 1))
    eje.set_xticklabels(etiquetas, fontsize=7, rotation=45, ha="right")
    eje.set_yscale("log")
    eje.yaxis.set_major_formatter(FuncFormatter(_formato_miles))
    eje.set_title(
        "Figura 2. Variabilidad y valores extremos de casos registrados (IPC) por año",
        fontsize=12, fontweight="bold",
    )
    eje.set_xlabel("Año (n = estados con dato)")
    eje.set_ylabel("Casos registrados por estado (escala logarítmica)")
    eje.grid(True, axis="y", linestyle="--", alpha=0.5)
    _guardar(figura, ruta)

# Figura 3: dispersion por grupos
def figura3_dispersion_grupos(df, ruta, top=5):
    casos = _unicos(_total_ipc(df, "cases_registered"), ["state", "year"])
    casos = casos[["state", "year", "value"]].rename(columns={"value": "casos"})
    detenidos = _unicos(_total_ipc(df, "persons_arrested"), ["state", "year"])
    detenidos = detenidos[["state", "year", "value"]].rename(columns={"value": "detenidos"})
    pares = casos.merge(detenidos, on=["state", "year"])
    pares = pares[(pares["casos"] > 0) & (pares["detenidos"] > 0)]
    grupos = pares.groupby("state")["casos"].sum().nlargest(top).index
    resto = pares[~pares["state"].isin(grupos)]
    _estilo()
    figura, eje = plt.subplots(figsize=(10, 6.5))
    eje.scatter(resto["casos"], resto["detenidos"], s=30, color="lightgray",
                edgecolors="gray", linewidths=0.5, label="Otros estados")
    colores = plt.cm.tab10(np.arange(len(grupos)))
    for estado, color in zip(grupos, colores):
        grupo = pares[pares["state"] == estado]
        eje.scatter(grupo["casos"], grupo["detenidos"], s=45, color=color,
                    edgecolors="black", linewidths=0.5, label=estado)
    eje.set_xscale("log")
    eje.set_yscale("log")
    eje.xaxis.set_major_formatter(FuncFormatter(_formato_miles))
    eje.yaxis.set_major_formatter(FuncFormatter(_formato_miles))
    eje.set_title(
        "Figura 3. Casos registrados vs. personas detenidas por estado y año (IPC)",
        fontsize=12, fontweight="bold",
    )
    eje.set_xlabel("Casos registrados (escala logarítmica)")
    eje.set_ylabel("Personas detenidas (escala logarítmica)")
    eje.grid(True, which="both", linestyle="--", alpha=0.4)
    eje.legend(title=f"Grupo: top {top} estados por casos", fontsize=8, loc="upper left")
    _guardar(figura, ruta)

# Figura 4: Comparacion de estados
def figura4_top_estados(df, ruta, n=10):
    casos = _unicos(_total_ipc(df, "cases_registered"), ["state", "year"])
    resumen = (
        casos.groupby("state")["value"]
        .agg(total="sum", años="nunique")
        .nlargest(n, "total")
        .sort_values("total")
    )
    etiquetas = [f"{estado} ({cantidad} años)" for estado, cantidad in zip(resumen.index, resumen["años"])]
    _estilo()
    figura, eje = plt.subplots(figsize=(10, 6))
    barras = eje.barh(etiquetas, resumen["total"], color="#348abd",
                      edgecolor="black", alpha=0.85)
    for barra in barras:
        eje.text(barra.get_width() * 1.01, barra.get_y() + barra.get_height() / 2,
                 f"{barra.get_width():,.0f}", va="center", ha="left", fontsize=9)
    eje.set_xlim(0, resumen["total"].max() * 1.15)
    eje.xaxis.set_major_formatter(FuncFormatter(_formato_miles))
    eje.set_title(
        f"Figura 4. Top {n} estados por casos registrados acumulados (IPC)",
        fontsize=12, fontweight="bold",
    )
    eje.set_xlabel("Casos registrados acumulados (suma de todos los años disponibles)")
    eje.set_ylabel("Estado / Unión Territorial (años con datos)")
    eje.grid(True, axis="x", linestyle="--", alpha=0.5)
    _guardar(figura, ruta)

# Figura 5: relacion entre variables
def figura5_correlacion(df, ruta):
    subconjunto = df[
        (df["scope"] == SCOPE_IPC)
        & (df["crime_head"].isin(TOTALES_IPC))
        & (df["metric"].isin(list(ETIQUETAS_METRICAS)))
    ]
    subconjunto = _unicos(subconjunto, ["state", "year", "metric"])
    pivote = subconjunto.pivot(index=["state", "year"], columns="metric", values="value")
    pivote = pivote[[metrica for metrica in ETIQUETAS_METRICAS if metrica in pivote.columns]]
    pivote = pivote.rename(columns=ETIQUETAS_METRICAS)
    correlacion = pivote.corr(method="pearson")
    _estilo()
    figura, eje = plt.subplots(figsize=(9.5, 8))
    imagen = eje.imshow(correlacion.values, cmap="RdBu_r", vmin=-1, vmax=1)
    eje.grid(False)
    eje.set_xticks(range(len(correlacion.columns)))
    eje.set_xticklabels(correlacion.columns, rotation=40, ha="right", fontsize=9)
    eje.set_yticks(range(len(correlacion.index)))
    eje.set_yticklabels(correlacion.index, fontsize=9)
    for fila in range(len(correlacion.index)):
        for columna in range(len(correlacion.columns)):
            valor = correlacion.iloc[fila, columna]
            eje.text(columna, fila, f"{valor:.2f}", ha="center", va="center", fontsize=9,
                     fontweight="bold",
                     color="white" if abs(valor) > 0.6 else "black")
    barra_color = figura.colorbar(imagen, ax=eje, shrink=0.8)
    barra_color.set_label("Coeficiente de Pearson (de -1 a 1)", fontsize=10)
    eje.set_title("Figura 5. Correlación entre métricas principales (total IPC)",
                  fontsize=12, fontweight="bold", pad=12)
    eje.set_xlabel("Métrica")
    eje.set_ylabel("Métrica")
    _guardar(figura, ruta)

# Figura 6: PREGUNTA DE EQUIPO crecimiento por tipo de delito
def figura6_pregunta_crecimiento(df, ruta, base_minima=1000, n_años=3):
    años = sorted(df["year"].dropna().unique())
    años_inicio = años[:n_años]
    años_fin = años[-n_años:]
    periodo_inicio = f"{int(años_inicio[0])}-{int(años_inicio[-1])}"
    periodo_fin = f"{int(años_fin[0])}-{int(años_fin[-1])}"
    subconjunto = df[
        (df["metric"] == "cases_registered")
        & (df["scope"] == SCOPE_IPC)
        & (~df["crime_category"].isin([CATEGORIA_TOTAL, "other"]))
        & (~df["crime_head"].isin(TOTALES_IPC))
    ]
    subconjunto = _unicos(subconjunto, ["state", "year", "crime_head"])

    años_por_estado = subconjunto.groupby("state")["year"].nunique()
    estados_completos = años_por_estado[años_por_estado == len(años)].index
    subconjunto = subconjunto[subconjunto["state"].isin(estados_completos)]

    por_año = subconjunto.groupby(["crime_category", "year"])["value"].sum().unstack("year")
    tabla = pd.DataFrame({
        "promedio_inicio": por_año[años_inicio].mean(axis=1),
        "promedio_fin": por_año[años_fin].mean(axis=1),
    }).dropna()
    tabla = tabla[tabla["promedio_inicio"] >= base_minima]
    tabla["cambio_%"] = (tabla["promedio_fin"] - tabla["promedio_inicio"]) / tabla["promedio_inicio"] * 100
    tabla = tabla.sort_values("cambio_%")
    if tabla.empty:
        logging.warning("Ninguna categoria cumple los criterios; no se genera la figura.")
        return

    _estilo()
    figura, eje = plt.subplots(figsize=(11, 6.5))
    etiquetas = [
        f"{categoria.replace('_', ' ').capitalize()}\n"
        f"({fila['promedio_inicio']:,.0f} → {fila['promedio_fin']:,.0f} casos/año)"
        for categoria, fila in tabla.iterrows()
    ]
    colores = ["#d95f02" if cambio > 0 else "#1b9e77" for cambio in tabla["cambio_%"]]
    barras = eje.barh(etiquetas, tabla["cambio_%"], color=colores, edgecolor="black", alpha=0.85)
    for barra in barras:
        ancho = barra.get_width()
        eje.text(ancho, barra.get_y() + barra.get_height() / 2, f" {ancho:,.0f}%",
                 va="center", ha="left" if ancho >= 0 else "right", fontsize=9)
    eje.axvline(0, color="black", linewidth=1)
    eje.set_title(
        f"Figura 6. Cambio porcentual de casos registrados por tipo de delito IPC\n"
        f"Promedio {periodo_inicio} vs. promedio {periodo_fin}",
        fontsize=12, fontweight="bold",
    )
    eje.set_xlabel("Cambio porcentual entre promedios (%)")
    eje.set_ylabel(f"Tipo de delito (casos promedio por año: {periodo_inicio} → {periodo_fin})")
    eje.grid(True, axis="x", linestyle="--", alpha=0.5)
    _guardar(figura, ruta)

def generar_visualizaciones(df, ruta_salida_figuras=DIR_FIGURAS):
    ruta_figuras = Path(ruta_salida_figuras)
    ruta_figuras.mkdir(parents=True, exist_ok=True)
    logging.info("Generando visualizaciones con Matplotlib...")
    figura1_distribucion(df, ruta_figuras / "figura1_distribucion.png")
    figura2_valores_extremos(df, ruta_figuras / "figura2_valores_extremos.png")
    figura3_dispersion_grupos(df, ruta_figuras / "figura3_dispersion.png")
    figura4_top_estados(df, ruta_figuras / "figura4_top_estados.png")
    figura5_correlacion(df, ruta_figuras / "figura5_matriz_correlacion.png")
    figura6_pregunta_crecimiento(df, ruta_figuras / "figura6_pregunta_crecimiento.png")
    logging.info("Visualizaciones completadas.")
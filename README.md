
# Laboratorio 04 — Análisis Exploratorio de Datos con Python

**Asignatura:** Big Data  
**Carrera:** Ingeniería Civil Informática  
**Institución:** Universidad Autónoma de Chile  
**Fecha:** Octubre de 2026

## 📖 Descripción

Este repositorio contiene el desarrollo del **Laboratorio 04 de Big Data**, centrado en un análisis exploratorio de datos (EDA) de estadísticas delictivas de la India, obtenidas del conjunto de datos **CrimeBase**, basado en publicaciones del *National Crime Records Bureau* (NCRB).

El proyecto abarca las siguientes etapas:

- Carga e inspección de datos.
- Diagnóstico de calidad.
- Limpieza y preparación de datos.
- Estadística descriptiva.
- Análisis de relaciones entre variables.
- Generación de visualizaciones.

## 📊 Datos y resultados

El conjunto de datos utilizado contiene:

- **668.240 registros** y **12 columnas**.
- Registros delictivos correspondientes al período 2001–2022.
- Información sobre casos registrados, personas detenidas, condenas y víctimas.

Entre los principales resultados obtenidos destacan:

- Identificación de valores faltantes y potenciales valores atípicos.
- Análisis estadístico por métrica.
- Comparación descriptiva entre estados.
- Estudio de correlaciones entre casos registrados y personas detenidas.
- Generación de **seis visualizaciones** y tablas de resultados reproducibles.

**Nota:** Las asociaciones estadísticas identificadas no implican causalidad. Tampoco es posible calcular tasas de criminalidad por habitante sin incorporar información poblacional.

## 📁 Estructura del repositorio

Todo el código y los resultados se encuentran en [`proyecto_eda/`](proyecto_eda/).

```text
Big-Data_lab04/
├── README.md
├── .gitignore
└── proyecto_eda/
    ├── README.md
    ├── requirements.txt
    ├── analisis_exploratorio.py
    ├── visualizaciones.py
    ├── datos/
    │   ├── crime_state_year.zip
    │   └── DATA_DICTIONARY.md
    └── resultados/
        ├── tablas/
        └── figuras/
```

## 🛠️ Tecnologías utilizadas

| Tecnología | Versión |
|------------|---------|
| Python | 3.11.13 |
| pandas | 2.2.3 |
| NumPy | 1.26.4 |
| Matplotlib | 3.11.2 |
| Seaborn | 0.13.2 |

También se utilizaron Visual Studio Code, Git y GitHub para el desarrollo y control de versiones.

## 🚀 Ejecución rápida

Desde la raíz del repositorio, abre una terminal y ejecuta:

**1. Acceder al directorio del proyecto:**

```cmd
cd proyecto_eda
```

**2. Instalar las dependencias:**

```cmd
python -m pip install -r requirements.txt
```

**3. Ejecutar el análisis:**

```cmd
python analisis_exploratorio.py
```

El programa lee directamente el archivo comprimido `datos/crime_state_year.zip`, sin necesidad de descomprimirlo manualmente.

Los resultados generados se almacenan en:

- `resultados/tablas/`: archivos CSV con diagnósticos y estadísticas.
- `resultados/figuras/`: seis visualizaciones en formato PNG.

### 📚 Documentación completa

Para consultar las instrucciones detalladas de instalación, uso de entornos virtuales, metodología y reproducción del análisis, revisa el siguiente archivo:

**[Ver documentación técnica del proyecto](proyecto_eda/README.md)**

## 👥 Integrantes

- Patricio Chaug
- José Arguello
- Javiera Fuentealba
- Samuel López

## 🔗 Fuente de los datos

**CrimeBase — India Crime Data: NCRB Statistics & News**

Disponible en [Kaggle](https://www.kaggle.com/datasets/chandranshbinjola/crimebase/data).

El conjunto de datos se basa en estadísticas del *National Crime Records Bureau* de la India.

Para mayor información sobre su procedencia, condiciones de uso y limitaciones, consultar la documentación del conjunto de datos y el informe del laboratorio.

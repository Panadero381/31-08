"""
App básica de Streamlit — Nivel de ríos/quebradas (CORNARE / MARCO)
--------------------------------------------------------------------
Cada estudiante debe cambiar, como mínimo, el código de la estación
en el sidebar. Los valores de fecha y calidad también son ajustables.

Para correrla:
    streamlit run app_nivel_cornare.py
"""

import requests
import pandas as pd
import numpy as np
import streamlit as st
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ------------------------------------------------------------------
# Coordenadas por defecto (Institución Universitaria Pascual Bravo)
# Se usan solo si la API no trae la latitud/longitud de la estación.
# ------------------------------------------------------------------
LAT_DEFECTO = 5.53489
LON_DEFECTO = -75.20548

API_BASE_URL = "https://marco.cornare.gov.co/api/v1/estaciones"

LLAVE_FECHA = "level_date"
LLAVE_VALOR = "level"
CANDIDATOS_LAT = ["lat", "latitude", "latitud"]
CANDIDATOS_LON = ["lng", "lon", "longitude", "longitud"]

st.set_page_config(page_title="Estacion Nariño, Río Venus", page_icon="🌊", layout="wide")
# Imagen principal de la aplicación
st.image(
    "data:image/jpeg;base64,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",
    caption="Río Venus - Estación de monitoreo",
    use_container_width=True
    width=300
    height=250
)


# ------------------------------------------------------------------
# Funciones de consulta
# ------------------------------------------------------------------
def obtener_serie_nivel(codigo_estacion, desde, hasta, calidad=1, timeout=30):
    url = f"{API_BASE_URL}/{codigo_estacion}/nivel"
    params = {"desde": desde, "hasta": hasta, "calidad": calidad}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout, verify=False)
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"HTTP {resp.status_code}"
    except requests.exceptions.RequestException as e:
        return None, f"Error de red: {e}"


def obtener_todas_las_paginas(datos_json, timeout=30):
    registros = list(datos_json.get("values", []))
    siguiente_url = datos_json.get("next")
    while siguiente_url:
        try:
            resp = requests.get(siguiente_url, timeout=timeout, verify=False)
        except requests.exceptions.RequestException:
            break
        if resp.status_code != 200:
            break
        pagina = resp.json()
        registros.extend(pagina.get("values", []))
        siguiente_url = pagina.get("next")
    return registros


def detectar_coordenadas(datos_json):
    """Busca lat/lon en las llaves raíz de la respuesta. Si no las encuentra, usa el valor por defecto."""
    if not isinstance(datos_json, dict):
        return LAT_DEFECTO, LON_DEFECTO, False

    lat = next((datos_json[k] for k in CANDIDATOS_LAT if k in datos_json), None)
    lon = next((datos_json[k] for k in CANDIDATOS_LON if k in datos_json), None)

    if lat is not None and lon is not None:
        try:
            return float(lat), float(lon), True
        except (TypeError, ValueError):
            pass
    return LAT_DEFECTO, LON_DEFECTO, False


def calcular_indice_calidad(df):
    """Índice simple (0-100) combinando completitud de la serie y proporción de outliers."""
    if df.empty or len(df) < 2:
        return 0.0, 0, 0

    df_idx = df.set_index("fecha")
    frecuencia_tipica = df["fecha"].diff().dropna().mode()
    if len(frecuencia_tipica) == 0:
        return 0.0, 0, 0
    frecuencia_tipica = frecuencia_tipica[0]

    rango_completo = pd.date_range(start=df_idx.index.min(), end=df_idx.index.max(), freq=frecuencia_tipica)
    esperados = len(rango_completo)
    huecos = esperados - len(df_idx)
    completitud = max(0.0, 1 - (huecos / esperados)) if esperados > 0 else 0.0

    Q1, Q3 = df["nivel"].quantile(0.25), df["nivel"].quantile(0.75)
    IQR = Q3 - Q1
    lim_inf, lim_sup = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    es_outlier = (df["nivel"] < lim_inf) | (df["nivel"] > lim_sup) | (df["nivel"] < 0)
    proporcion_outliers = es_outlier.mean()

    indice = (completitud * 0.7 + (1 - proporcion_outliers) * 0.3) * 100
    return round(indice, 1), int(huecos), int(es_outlier.sum())


# ------------------------------------------------------------------
# Sidebar — parámetros de la consulta (editables por cada estudiante)
# ------------------------------------------------------------------
st.sidebar.header("Parámetros de tu consulta")
nombre_estudiante = st.sidebar.text_input("Nombre del estudiante", "Kevin Alexander Londoño Berrio")
codigo_estacion = st.sidebar.text_input("Código de estación", "20")
fecha_desde = st.sidebar.date_input("Desde", pd.to_datetime("2026-08-25")).strftime("%Y-%m-%d")
fecha_hasta = st.sidebar.date_input("Hasta", pd.to_datetime("2026-08-31")).strftime("%Y-%m-%d")
calidad = st.sidebar.selectbox("Calidad", [1, 0], index=0, help="1 = solo datos validados")
consultar = st.sidebar.button("🔍 Consultar", type="primary")

st.title("🌊 Nivel de ríos y quebradas - Nariño, Río Venus")
st.caption(f"Estudiante: **{nombre_estudiante}** · Estación: **{codigo_estacion}**")

# ------------------------------------------------------------------
# Consulta y procesamiento
# ------------------------------------------------------------------
if consultar:
    with st.spinner("Consultando la API..."):
        datos_crudos, error = obtener_serie_nivel(codigo_estacion, fecha_desde, fecha_hasta, calidad)

    if error:
        st.error(f"❌ {error}")
    else:
        registros = obtener_todas_las_paginas(datos_crudos)

        if not registros:
            st.warning("No hay registros para esta estación y rango de fechas. Prueba otro código u otro rango.")
        else:
            df = pd.DataFrame(registros)
            df = df.rename(columns={LLAVE_FECHA: "fecha", LLAVE_VALOR: "nivel"})
            df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
            df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce")
            df = df.dropna(subset=["fecha", "nivel"]).sort_values("fecha").reset_index(drop=True)

            lat, lon, coords_reales = detectar_coordenadas(datos_crudos)
            indice_calidad, huecos, n_outliers = calcular_indice_calidad(df)

            # --- Métricas principales ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Lecturas", len(df))
            col2.metric("Nivel promedio", f"{df['nivel'].mean():.2f}")
            col3.metric("Índice de calidad", f"{indice_calidad} / 100")
            col4.metric("Outliers detectados", n_outliers)

            # --- Gráfico de la serie ---
            st.subheader("Serie de nivel")
            st.line_chart(df.set_index("fecha")["nivel"])

            # --- Mapa de la estación ---
            st.subheader("Ubicación de la estación")
            if not coords_reales:
                st.caption("La API no trajo latitud/longitud de la estación — se muestra el punto de partida (Pascual Bravo). Ajusta `CANDIDATOS_LAT` / `CANDIDATOS_LON` si conoces el nombre real de esas llaves.")
            st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=10)

            # --- Detalle de calidad ---
            with st.expander("Detalle del índice de calidad"):
                st.write(f"- Huecos de reporte detectados: **{huecos}**")
                st.write(f"- Outliers (IQR + nivel negativo): **{n_outliers}** de {len(df)} lecturas")
                st.write("El índice combina completitud de la serie (70%) y proporción de datos sin outliers (30%).")

            # --- Tabla y descarga ---
            with st.expander("Ver datos crudos"):
                st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Descargar CSV", csv, file_name=f"nivel_estacion_{codigo_estacion}.csv", mime="text/csv")
else:
    st.info("Ajusta los parámetros en el sidebar y presiona **Consultar**.")

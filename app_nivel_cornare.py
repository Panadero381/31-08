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
# CONFIGURACIÓN
# ------------------------------------------------------------------

st.set_page_config(
    page_title="Estación Nariño - Río Venus",
    page_icon="🌊",
    layout="wide"
)


# ------------------------------------------------------------------
# ESTILOS
# ------------------------------------------------------------------
st.markdown("""
<style>

    /* Fondo general */
    .stApp {
        background-color: #f4f8fb;
        color: #000000;
    }

    /* Títulos */
    h1, h2, h3, h4, h5, h6 {
        color: #000000;
    }

    /* Encabezado principal */
    .titulo-principal {
        background-color: #0b5e75;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
    }

    .titulo-principal h1 {
        color: white !important;
        margin-bottom: 5px;
        font-size: 32px;
    }

    .titulo-principal p {
        color: white !important;
        font-size: 16px;
        margin: 0;
    }

    /* Tarjetas */
    .tarjeta {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #d9e5eb;
        margin-bottom: 15px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    }

    .tarjeta h3 {
        color: #0b5e75 !important;
        margin-bottom: 8px;
    }

    .tarjeta p {
        color: #000000 !important;
        margin: 0;
    }

    /* Métricas */
    [data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #d9e5eb;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
    }

    [data-testid="stMetricLabel"] {
        color: #000000 !important;
    }

    [data-testid="stMetricValue"] {
        color: #000000 !important;
    }

    /* Texto secundario */
    .stCaption {
        color: #000000 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #000000 !important;
    }

    /* Campos de texto */
    input {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    div[data-baseweb="select"] * {
        color: #000000 !important;
    }

    /* Botones */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        padding: 10px;
    }

    /* Expander */
    details {
        background-color: white;
        border-radius: 10px;
        border: 1px solid #d9e5eb;
    }

    details summary {
        color: #000000 !important;
    }

    /* Texto dentro de expander */
    details p,
    details li,
    details span {
        color: #000000 !important;
    }

    /* Tablas */
    [data-testid="stDataFrame"] {
        background-color: white;
    }

    /* Pie de página */
    .pie {
        text-align: center;
        color: #000000 !important;
        font-size: 13px;
        padding: 20px;
        margin-top: 30px;
    }

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# COORDENADAS POR DEFECTO
# ------------------------------------------------------------------

LAT_DEFECTO = 5.53489
LON_DEFECTO = -75.20548

API_BASE_URL = "https://marco.cornare.gov.co/api/v1/estaciones"

LLAVE_FECHA = "level_date"
LLAVE_VALOR = "level"

CANDIDATOS_LAT = ["lat", "latitude", "latitud"]
CANDIDATOS_LON = ["lng", "lon", "longitude", "longitud"]


# ------------------------------------------------------------------
# ENCABEZADO
# ------------------------------------------------------------------

st.markdown("""
<div class="titulo-principal">
    <h1>🌊 Nivel de ríos y quebradas</h1>
    <p>Estación Nariño - Río Venus | Datos de CORNARE / MARCO</p>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# IMAGEN PRINCIPAL
# ------------------------------------------------------------------

col_img1, col_img2, col_img3 = st.columns([1, 2, 1])

with col_img2:
    st.image(
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBalsokD_PD4fFVjVcrsGO8jcckz0pMeJWZmLxUmVMcC8GKBTGlX4Qk8w&s=10",
        caption="Estación Nariño - Río Venus",
        width=250
    )


# ------------------------------------------------------------------
# FUNCIONES DE CONSULTA
# ------------------------------------------------------------------

def obtener_serie_nivel(codigo_estacion, desde, hasta, calidad=1, timeout=30):

    url = f"{API_BASE_URL}/{codigo_estacion}/nivel"

    params = {
        "desde": desde,
        "hasta": hasta,
        "calidad": calidad
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }

    try:

        resp = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout,
            verify=False
        )

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

            resp = requests.get(
                siguiente_url,
                timeout=timeout,
                verify=False
            )

        except requests.exceptions.RequestException:
            break

        if resp.status_code != 200:
            break

        pagina = resp.json()

        registros.extend(
            pagina.get("values", [])
        )

        siguiente_url = pagina.get("next")

    return registros


def detectar_coordenadas(datos_json):

    if not isinstance(datos_json, dict):
        return LAT_DEFECTO, LON_DEFECTO, False

    lat = next(
        (datos_json[k] for k in CANDIDATOS_LAT if k in datos_json),
        None
    )

    lon = next(
        (datos_json[k] for k in CANDIDATOS_LON if k in datos_json),
        None
    )

    if lat is not None and lon is not None:

        try:
            return float(lat), float(lon), True

        except (TypeError, ValueError):
            pass

    return LAT_DEFECTO, LON_DEFECTO, False


def calcular_indice_calidad(df):

    if df.empty or len(df) < 2:
        return 0.0, 0, 0

    df_idx = df.set_index("fecha")

    frecuencia_tipica = df["fecha"].diff().dropna().mode()

    if len(frecuencia_tipica) == 0:
        return 0.0, 0, 0

    frecuencia_tipica = frecuencia_tipica[0]

    rango_completo = pd.date_range(
        start=df_idx.index.min(),
        end=df_idx.index.max(),
        freq=frecuencia_tipica
    )

    esperados = len(rango_completo)

    huecos = esperados - len(df_idx)

    completitud = (
        max(0.0, 1 - (huecos / esperados))
        if esperados > 0
        else 0.0
    )

    Q1 = df["nivel"].quantile(0.25)
    Q3 = df["nivel"].quantile(0.75)

    IQR = Q3 - Q1

    lim_inf = Q1 - 1.5 * IQR
    lim_sup = Q3 + 1.5 * IQR

    es_outlier = (
        (df["nivel"] < lim_inf) |
        (df["nivel"] > lim_sup) |
        (df["nivel"] < 0)
    )

    proporcion_outliers = es_outlier.mean()

    indice = (
        completitud * 0.7 +
        (1 - proporcion_outliers) * 0.3
    ) * 100

    return round(indice, 1), int(huecos), int(es_outlier.sum())


# ------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------

st.sidebar.markdown("## ⚙️ Parámetros")

st.sidebar.markdown(
    "Configura los datos de la estación que deseas consultar."
)

nombre_estudiante = st.sidebar.text_input(
    "👤 Nombre del estudiante",
    "Kevin Alexander Londoño Berrio"
)

codigo_estacion = st.sidebar.text_input(
    "📍 Código de estación",
    "20"
)

fecha_desde = st.sidebar.date_input(
    "📅 Desde",
    pd.to_datetime("2026-08-25")
).strftime("%Y-%m-%d")

fecha_hasta = st.sidebar.date_input(
    "📅 Hasta",
    pd.to_datetime("2026-08-31")
).strftime("%Y-%m-%d")

calidad = st.sidebar.selectbox(
    "🔎 Calidad",
    [1, 0],
    index=0,
    help="1 = solo datos validados"
)

st.sidebar.markdown("---")

consultar = st.sidebar.button(
    "🔍 Consultar datos",
    type="primary"
)


# ------------------------------------------------------------------
# INFORMACIÓN DEL ESTUDIANTE
# ------------------------------------------------------------------

st.markdown(f"""
<div class="tarjeta">
    <h3>👨‍🎓 Información de la consulta</h3>
    <p><b>Estudiante:</b> {nombre_estudiante}</p>
    <p><b>Estación:</b> {codigo_estacion}</p>
    <p><b>Periodo:</b> {fecha_desde} → {fecha_hasta}</p>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# CONSULTA Y PROCESAMIENTO
# ------------------------------------------------------------------

if consultar:

    with st.spinner("🌊 Consultando los datos de CORNARE..."):

        datos_crudos, error = obtener_serie_nivel(
            codigo_estacion,
            fecha_desde,
            fecha_hasta,
            calidad
        )

    if error:

        st.error(f"❌ {error}")

    else:

        registros = obtener_todas_las_paginas(
            datos_crudos
        )

        if not registros:

            st.warning(
                "⚠️ No hay registros para esta estación y rango de fechas. "
                "Prueba otro código u otro rango."
            )

        else:

            df = pd.DataFrame(registros)

            df = df.rename(
                columns={
                    LLAVE_FECHA: "fecha",
                    LLAVE_VALOR: "nivel"
                }
            )

            df["fecha"] = pd.to_datetime(
                df["fecha"],
                errors="coerce"
            )

            df["nivel"] = pd.to_numeric(
                df["nivel"],
                errors="coerce"
            )

            df = df.dropna(
                subset=["fecha", "nivel"]
            ).sort_values(
                "fecha"
            ).reset_index(drop=True)

            lat, lon, coords_reales = detectar_coordenadas(
                datos_crudos
            )

            indice_calidad, huecos, n_outliers = calcular_indice_calidad(
                df
            )


            # ------------------------------------------------------
            # MÉTRICAS
            # ------------------------------------------------------

            st.subheader("📊 Resumen de datos")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "📈 Lecturas",
                len(df)
            )

            col2.metric(
                "💧 Nivel promedio",
                f"{df['nivel'].mean():.2f}"
            )

            col3.metric(
                "⭐ Índice de calidad",
                f"{indice_calidad} / 100"
            )

            col4.metric(
                "⚠️ Outliers",
                n_outliers
            )


            # ------------------------------------------------------
            # GRÁFICO
            # ------------------------------------------------------

            st.subheader("📈 Serie de nivel")

            st.markdown("""
            <div class="tarjeta">
                <p>
                Gráfico del comportamiento del nivel del río
                durante el periodo seleccionado.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.line_chart(
                df.set_index("fecha")["nivel"]
            )


            # ------------------------------------------------------
            # MAPA
            # ------------------------------------------------------

            st.subheader("📍 Ubicación de la estación")

            if not coords_reales:

                st.warning(
                    "La API no trajo latitud/longitud de la estación. "
                    "Se muestra el punto de referencia configurado."
                )

            mapa = pd.DataFrame({
                "lat": [lat],
                "lon": [lon]
            })

            st.map(
                mapa,
                zoom=10
            )


            # ------------------------------------------------------
            # CALIDAD
            # ------------------------------------------------------

            st.subheader("🔎 Calidad de los datos")

            with st.expander(
                "📋 Ver detalle del índice de calidad"
            ):

                st.write(
                    f"🕳️ Huecos de reporte detectados: "
                    f"**{huecos}**"
                )

                st.write(
                    f"⚠️ Outliers detectados: "
                    f"**{n_outliers}** de **{len(df)}** lecturas"
                )

                st.info(
                    "El índice combina la completitud de la serie "
                    "(70%) y la proporción de datos sin outliers (30%)."
                )


            # ------------------------------------------------------
            # DATOS
            # ------------------------------------------------------

            st.subheader("📋 Datos registrados")

            with st.expander(
                "👁️ Ver datos crudos"
            ):

                st.dataframe(
                    df,
                    use_container_width=True
                )


            # ------------------------------------------------------
            # DESCARGA
            # ------------------------------------------------------

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "⬇️ Descargar datos en CSV",
                csv,
                file_name=f"nivel_estacion_{codigo_estacion}.csv",
                mime="text/csv"
            )


else:

    st.markdown("""
    <div class="tarjeta">
        <h3>🌊 Consulta de información</h3>
        <p>
        Ajusta los parámetros en el menú lateral y presiona
        <b>🔍 Consultar datos</b> para obtener información
        sobre el nivel de la estación.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------------
# PIE DE PÁGINA
# ------------------------------------------------------------------

st.markdown("""
<div class="pie">
    🌊 Sistema de consulta de niveles de ríos y quebradas<br>
    CORNARE / MARCO · Proyecto académico
</div>
""", unsafe_allow_html=True)

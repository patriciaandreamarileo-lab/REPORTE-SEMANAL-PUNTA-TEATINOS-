import streamlit as st

from modules.navegacion import configurar_navegacion


# =========================================================
# 1. CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Reporte Semanal | Punta Teatinos",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# 2. PALETA DE COLORES
# =========================================================

COLOR_AZUL = "#102F4A"
COLOR_AZUL_ACTIVO = "#28465F"
COLOR_FONDO = "#F4F7FB"
COLOR_BLANCO = "#FFFFFF"


# =========================================================
# 3. ESTILOS GENERALES
# =========================================================

st.markdown(
    f"""
    <style>

    /* =========================================
       FONDO PRINCIPAL
    ========================================= */

    .stApp {{
        background-color: {COLOR_FONDO};
    }}

    .main .block-container {{
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}


    /* =========================================
       MENÚ LATERAL
    ========================================= */

    [data-testid="stSidebar"] {{
        background-color: {COLOR_AZUL} !important;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        background-color: {COLOR_AZUL} !important;
    }}

    /* Textos del menú */

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {{
        color: {COLOR_BLANCO} !important;
    }}

    /* Enlaces */

    [data-testid="stSidebar"] a {{
        color: {COLOR_BLANCO} !important;
        border-radius: 8px !important;
    }}

    [data-testid="stSidebar"] a p {{
        color: {COLOR_BLANCO} !important;
    }}

    /* Página seleccionada */

    [data-testid="stSidebar"] [aria-current="page"] {{
        background-color: {COLOR_AZUL_ACTIVO} !important;
        border-radius: 8px !important;
    }}

    [data-testid="stSidebar"] [aria-current="page"] p {{
        color: {COLOR_BLANCO} !important;
        font-weight: 700 !important;
    }}

    /* Efecto hover */

    [data-testid="stSidebar"] a:hover {{
        background-color: {COLOR_AZUL_ACTIVO} !important;
    }}

    /* Iconos */

    [data-testid="stSidebar"] svg {{
        color: {COLOR_BLANCO} !important;
    }}

    /* Botones del menú */

    [data-testid="stSidebar"] button {{
        color: {COLOR_BLANCO} !important;
    }}

    /* Separadores */

    [data-testid="stSidebar"] hr {{
        border-color: #496176 !important;
    }}


    /* =========================================
       ELEMENTOS GENERALES
    ========================================= */

    .stButton > button {{
        border-radius: 8px;
        font-weight: 600;
    }}

    /* Ocultar pie de página de Streamlit */

    footer {{
        visibility: hidden;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 4. NAVEGACIÓN
# =========================================================

configurar_navegacion()

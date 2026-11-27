import streamlit as st

from modules.navegacion import configurar_navegacion


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Reporte Semanal | Punta Teatinos",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# PALETA DE COLORES
# =========================================================

COLOR_AZUL = "#102F4A"
COLOR_AZUL_ACTIVO = "#28465F"
COLOR_FONDO = "#F4F7FB"
COLOR_BLANCO = "#FFFFFF"


# =========================================================
# ESTILOS GENERALES
# =========================================================

st.markdown(f"""
<style>

/* =====================================================
   FONDO PRINCIPAL
===================================================== */

.stApp {{
    background-color: {COLOR_FONDO};
}}

.main .block-container {{
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}}


/* =====================================================
   MENÚ LATERAL
===================================================== */

[data-testid="stSidebar"] {{
    background-color: {COLOR_AZUL} !important;
}}

/* Fondo de todo el contenido del menú */
[data-testid="stSidebar"] > div:first-child {{
    background-color: {COLOR_AZUL} !important;
}}

/* Títulos y textos del menú */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {{
    color: {COLOR_BLANCO} !important;
}}

/* Encabezados de las secciones */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    color: {COLOR_BLANCO} !important;
}}

/* Enlaces de navegación */
[data-testid="stSidebar"] a {{
    color: {COLOR_BLANCO} !important;
    border-radius: 8px !important;
    transition: background-color 0.2s ease;
}}

/* Texto de los enlaces */
[data-testid="stSidebar"] a p {{
    color: {COLOR_BLANCO} !important;
}}

/* Opción seleccionada */
[data-testid="stSidebar"] [aria-current="page"] {{
    background-color: {COLOR_AZUL_ACTIVO} !important;
    border-radius: 8px !important;
}}

/* Texto de la opción seleccionada */
[data-testid="stSidebar"] [aria-current="page"] p {{
    color: {COLOR_BLANCO} !important;
    font-weight: 700 !important;
}}

/* Efecto al pasar el cursor */
[data-testid="stSidebar"] a:hover {{
    background-color: {COLOR_AZUL_ACTIVO} !important;
}}

/* Iconos */
[data-testid="stSidebar"] svg {{
    color: {COLOR_BLANCO} !important;
}}

/* Botones del menú lateral */
[data-testid="stSidebar"] button {{
    color: {COLOR_BLANCO} !important;
}}

/* Separadores */
[data-testid="stSidebar"] hr {{
    border-color: #496176 !important;
}}


/* =====================================================
   BOTONES GENERALES
===================================================== */

.stButton > button {{
    border-radius: 8px;
    font-weight: 600;
}}


/* =====================================================
   PIE DE PÁGINA
===================================================== */

footer {{
    visibility: hidden;
}}

</style>
""", unsafe_allow_html=True)


# =========================================================
# NAVEGACIÓN DEL DASHBOARD
# =========================================================

configurar_navegacion()

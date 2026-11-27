
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
# ESTILOS GENERALES Y MENÚ LATERAL
# =========================================================

st.markdown("""
<style>

/* -----------------------------------------------------
   FONDO GENERAL
----------------------------------------------------- */

.stApp {
    background-color: #F4F7FB;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}


/* -----------------------------------------------------
   MENÚ LATERAL
----------------------------------------------------- */

[data-testid="stSidebar"] {
    background-color: #173B5E !important;
}

/* Contenido del menú lateral */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
}

/* Títulos de las secciones:
   GENERAL, ANÁLISIS y ADMINISTRACIÓN */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #FFFFFF !important;
}

/* Enlaces de navegación */
[data-testid="stSidebar"] a {
    color: #FFFFFF !important;
    border-radius: 8px;
}

/* Texto de las opciones */
[data-testid="stSidebar"] a p {
    color: #FFFFFF !important;
}

/* Opción seleccionada */
[data-testid="stSidebar"] [aria-current="page"] {
    background-color: #286B9E !important;
    border-radius: 8px;
}

/* Texto de la opción seleccionada */
[data-testid="stSidebar"] [aria-current="page"] p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* Efecto al pasar el cursor */
[data-testid="stSidebar"] a:hover {
    background-color: #245477 !important;
}

/* Iconos del menú */
[data-testid="stSidebar"] svg {
    color: #FFFFFF !important;
    fill: none;
}

/* Botón para contraer el menú */
[data-testid="stSidebar"] button {
    color: #FFFFFF !important;
}


/* -----------------------------------------------------
   COLOR DE LOS SEPARADORES
----------------------------------------------------- */

[data-testid="stSidebar"] hr {
    border-color: #42617D;
}


/* -----------------------------------------------------
   PIE DE PÁGINA
----------------------------------------------------- */

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# NAVEGACIÓN
# =========================================================

configurar_navegacion()

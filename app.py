import streamlit as st

from modules.navegacion import configurar_navegacion


# =====================================================
# 1. CONFIGURACIÓN GENERAL
# =====================================================

st.set_page_config(
    page_title="Reporte Semanal | Punta Teatinos",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. IDENTIDAD DEL DASHBOARD
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #F4F7FB;
}

[data-testid="stSidebar"] {
    background-color: #FFFFFF;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. INICIAR NAVEGACIÓN
# =====================================================

configurar_navegacion()


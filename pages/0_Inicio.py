import streamlit as st


# =========================================================
# CONFIGURACIÓN VISUAL
# =========================================================

st.markdown("""
<style>
    .stApp {
        background-color: #F4F7FB;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* ENCABEZADO PRINCIPAL */
    .hero {
        background: linear-gradient(110deg, #153957 0%, #286B9E 100%);
        padding: 35px 38px;
        border-radius: 17px;
        margin-bottom: 48px;
        color: white;
    }

    .hero-title {
        font-size: 32px;
        font-weight: 800;
        color: white;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 16px;
        color: #F0F5FA;
    }

    /* TÍTULO DEL PANEL */
    .panel-title {
        font-size: 36px;
        font-weight: 800;
        color: #173B5E;
        margin-bottom: 12px;
    }

    .panel-description {
        font-size: 18px;
        color: #687E96;
        margin-bottom: 35px;
    }

    /* TARJETAS */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border: 1px solid #D9E0E8;
        border-radius: 12px;
        min-height: 300px;
    }

    .card-icon {
        font-size: 42px;
        margin-bottom: 22px;
    }

    .card-title {
        color: #173B5E;
        font-size: 23px;
        font-weight: 800;
        margin-bottom: 20px;
    }

    .card-description {
        color: #687E96;
        font-size: 15px;
        line-height: 1.8;
        min-height: 78px;
    }

    /* ENLACES */
    div[data-testid="stPageLink"] a {
        color: #173B5E !important;
        font-size: 15px;
        font-weight: 500;
        text-decoration: none !important;
    }

    div[data-testid="stPageLink"] a:hover {
        color: #98643A !important;
    }

    /* PIE DE PÁGINA */
    .footer {
        text-align: center;
        color: #8A98A8;
        font-size: 12px;
        margin-top: 55px;
        padding-top: 18px;
        border-top: 1px solid #DCE4EF;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# ENCABEZADO
# =========================================================

st.markdown("""
<div class="hero">
    <div class="hero-title">
        DASHBOARD DE GESTIÓN DE MATERIAS PRIMAS
    </div>
    <div class="hero-subtitle">
        ENAEX CHILE | Planificación, consumo y análisis de precios
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# PANEL DE CONTROL
# =========================================================

st.markdown("""
<div class="panel-title">
    Panel de control
</div>

<div class="panel-description">
    Selecciona el módulo que deseas consultar para acceder a los
    análisis de materias primas.
</div>
""", unsafe_allow_html=True)


# =========================================================
# TARJETAS DE NAVEGACIÓN
# =========================================================

col1, col2, col3 = st.columns(3, gap="large")


# ---------------------------------------------------------
# TARJETA 1: ANÁLISIS POR PLANTA
# ---------------------------------------------------------

with col1:
    with st.container(border=True):
        st.markdown("""
        <div class="card-icon">🏭</div>

        <div class="card-title">
            Análisis por planta
        </div>

        <div class="card-description">
            Consulta los indicadores de inventario, cobertura,
            nivel de servicio y situación de las materias primas
            de la planta Punta Teatinos.
        </div>
        """, unsafe_allow_html=True)

        st.page_link(
            "pages/1_Analisis_por_planta.py",
            label="➡️ Ingresar al análisis"
        )


# ---------------------------------------------------------
# TARJETA 2: CONSUMO PROMEDIO
# ---------------------------------------------------------

with col2:
    with st.container(border=True):
        st.markdown("""
        <div class="card-icon">📊</div>

        <div class="card-title">
            Consumo promedio
        </div>

        <div class="card-description">
            Analiza el comportamiento histórico del consumo,
            sus variaciones mensuales y las tendencias de
            las materias primas.
        </div>
        """, unsafe_allow_html=True)

        st.page_link(
            "pages/2_Consumo_promedio.py",
            label="➡️ Ingresar al consumo"
        )


# ---------------------------------------------------------
# TARJETA 3: EVOLUCIÓN DE PRECIOS
# ---------------------------------------------------------

with col3:
    with st.container(border=True):
        st.markdown("""
        <div class="card-icon">📈</div>

        <div class="card-title">
            Evolución de precios
        </div>

        <div class="card-description">
            Visualiza la evolución de los precios de compra,
            las variaciones de las órdenes de compra y el
            comportamiento de los proveedores.
        </div>
        """, unsafe_allow_html=True)

        st.page_link(
            "pages/3_Evolucion_de_precios.py",
            label="➡️ Ingresar a precios"
        )


# =========================================================
# PIE DE PÁGINA
# =========================================================

st.markdown("""
<div class="footer">
    ENAEX CHILE | REPORTE SEMANAL | PUNTA TEATINOS
</div>
""", unsafe_allow_html=True)

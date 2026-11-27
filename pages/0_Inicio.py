import streamlit as st
import streamlit.components.v1 as components

from modules.mrp_reader import cargar_mrp


# =========================================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Inicio | Punta Teatinos",
    page_icon="🏭",
    layout="wide"
)

COLOR_PLANTA = "#98643A"
FONDO = "#F4F7FB"


# =========================================================
# ESTILOS
# =========================================================

st.markdown("""
<style>
    .stApp {
        background-color: #F4F7FB;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    .header-title {
        color: #17365D;
        font-size: 30px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .header-subtitle {
        color: #60758D;
        font-size: 18px;
        margin-bottom: 42px;
    }

    .plant-card {
        background-color: #FFFFFF;
        border: 1px solid #DCE4EF;
        border-left: 6px solid #98643A;
        border-radius: 15px;
        padding: 28px 30px;
        margin-bottom: 22px;
    }

    .plant-name {
        color: #98643A;
        font-size: 27px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .plant-info {
        color: #60758D;
        font-size: 16px;
    }

    .section-title {
        color: #24364B;
        font-size: 25px;
        font-weight: 750;
        margin-top: 15px;
        margin-bottom: 18px;
    }

    .info-card {
        background-color: #FFFFFF;
        border: 1px solid #DCE4EF;
        border-radius: 14px;
        padding: 23px 25px;
        min-height: 150px;
    }

    .info-title {
        color: #98643A;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 1px;
        margin-bottom: 13px;
    }

    .info-value {
        color: #26384D;
        font-size: 21px;
        font-weight: 700;
    }

    .description-card {
        background-color: #FFFFFF;
        border: 1px solid #DCE4EF;
        border-radius: 14px;
        padding: 25px 28px;
        margin-top: 28px;
        color: #52657A;
        font-size: 15px;
        line-height: 1.7;
    }

    .description-title {
        color: #24364B;
        font-size: 21px;
        font-weight: 750;
        margin-bottom: 12px;
    }

    .footer {
        color: #8795A6;
        font-size: 12px;
        text-align: center;
        margin-top: 45px;
        padding-top: 18px;
        border-top: 1px solid #DCE4EF;
    }

    div.stButton > button {
        background-color: #98643A;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 9px 20px;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background-color: #80512F;
        color: white;
        border: none;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# ENCABEZADO
# =========================================================

st.markdown(
    '<div class="header-title">REPORTE SEMANAL</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="header-subtitle">'
    'ENAEX CHILE | GESTIÓN DE MATERIAS PRIMAS'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# PRESENTACIÓN DE LA PLANTA
# =========================================================

st.markdown("""
<div class="plant-card">
    <div class="plant-name">PUNTA TEATINOS</div>
    <div class="plant-info">
        Planta ubicada en La Serena, Región de Coquimbo.
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# INFORMACIÓN DE LA PLANTA
# =========================================================

st.markdown(
    '<div class="section-title">Información de la planta</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-card">
        <div class="info-title">CENTRO SAP</div>
        <div class="info-value">E026</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <div class="info-title">UBICACIÓN</div>
        <div class="info-value">La Serena</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-card">
        <div class="info-title">ÁREA RESPONSABLE</div>
        <div class="info-value">Materias Primas</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# DESCRIPCIÓN DEL DASHBOARD
# =========================================================

st.markdown("""
<div class="description-card">
    <div class="description-title">
        Acerca del reporte
    </div>
    Este dashboard permite consultar y analizar información
    relacionada con la gestión de materias primas de la planta
    Punta Teatinos. Su objetivo es facilitar el seguimiento de
    los niveles de inventario, el consumo de materiales y la
    evolución de precios, entregando información para apoyar
    la planificación y la toma de decisiones.
</div>
""", unsafe_allow_html=True)


# =========================================================
# VERIFICACIÓN DE CONEXIÓN CON MRP
# =========================================================

st.markdown(
    '<div class="section-title">Estado de conexión</div>',
    unsafe_allow_html=True
)

if st.button("Verificar conexión con MRP"):
    try:
        with st.spinner("Conectando con el archivo MRP..."):
            datos, hojas = cargar_mrp()

        if datos is not None and not datos.empty:
            st.success("Conexión con el archivo MRP realizada correctamente.")

            col_a, col_b = st.columns(2)

            with col_a:
                st.metric("Registros encontrados", len(datos))

            with col_b:
                st.metric("Hojas disponibles", len(hojas))

            with st.expander("Ver hojas disponibles"):
                for hoja in hojas:
                    st.write(f"• {hoja}")

        else:
            st.warning(
                "La conexión se realizó, pero no se encontraron "
                "registros en la hoja principal del MRP."
            )

    except Exception as e:
        st.error("No fue posible conectar con el archivo MRP.")
        st.caption(f"Detalle del error: {e}")


# =========================================================
# PIE DE PÁGINA
# =========================================================

st.markdown("""
<div class="footer">
    ENAEX CHILE | REPORTE SEMANAL | PUNTA TEATINOS
</div>
""", unsafe_allow_html=True)

import streamlit as st

from modules.mrp_reader import cargar_mrp


# =====================================================
# 1. CONFIGURACIÓN VISUAL
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #F4F7FB;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

.main-title {
    font-size: 32px;
    font-weight: 800;
    color: #17345F;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 15px;
    color: #64748B;
    margin-bottom: 25px;
}

.plant-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-left: 6px solid #98643A;
    border-radius: 12px;
    padding: 25px;
    margin-top: 15px;
}

.plant-name {
    color: #98643A;
    font-size: 25px;
    font-weight: 800;
}

.plant-info {
    color: #64748B;
    font-size: 15px;
}

.info-box {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px;
    min-height: 125px;
}

.info-title {
    color: #64748B;
    font-size: 13px;
    margin-bottom: 8px;
}

.info-value {
    color: #17345F;
    font-size: 20px;
    font-weight: 750;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 2. ENCABEZADO
# =====================================================

st.markdown(
    '<p class="main-title">REPORTE SEMANAL</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">'
    'ENAEX CHILE | GESTIÓN DE MATERIAS PRIMAS'
    '</p>',
    unsafe_allow_html=True
)


# =====================================================
# 3. IDENTIFICACIÓN DE LA PLANTA
# =====================================================

st.markdown("""
<div class="plant-card">

    <div class="plant-name">
        PUNTA TEATINOS
    </div>

    <div class="plant-info">
        Planta ubicada en La Serena, Región de Coquimbo.
    </div>

</div>
""", unsafe_allow_html=True)


# =====================================================
# 4. INFORMACIÓN GENERAL
# =====================================================

st.markdown("### Información de la planta")

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""
    <div class="info-box">

        <div class="info-title">
            CENTRO SAP
        </div>

        <div class="info-value">
            E026
        </div>

    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="info-box">

        <div class="info-title">
            UBICACIÓN
        </div>

        <div class="info-value">
            La Serena
        </div>

    </div>
    """, unsafe_allow_html=True)

with col3:

    st.markdown("""
    <div class="info-box">

        <div class="info-title">
            ÁREA RESPONSABLE
        </div>

        <div class="info-value">
            Materias Primas
        </div>

    </div>
    """, unsafe_allow_html=True)


# =====================================================
# 5. DESCRIPCIÓN
# =====================================================

st.markdown("---")

st.markdown("### Panel de control")

st.markdown("""
Este dashboard permite consultar y analizar la información
relacionada con la gestión de materias primas de Punta Teatinos.

A través de sus diferentes secciones se podrá revisar el estado
del inventario, los niveles de cobertura, el consumo de materiales
y la evolución histórica de sus precios.

La información se actualizará mediante los archivos Excel
administrados desde el módulo de Administración.
""")


# =====================================================
# 6. ESTADO DEL ARCHIVO MRP
# =====================================================

st.markdown("---")

st.markdown("### Estado de conexión con el MRP")

if st.button(
    "Verificar conexión con MRP",
    use_container_width=True
):

    try:

        datos, hojas = cargar_mrp()

        if datos.empty:

            st.warning(
                "El archivo MRP está disponible, "
                "pero no contiene registros."
            )

        else:

            st.success(
                "Conexión correcta con el archivo MRP."
            )

            st.write(
                f"Registros encontrados: {len(datos):,}"
            )

            st.write(
                "Hojas disponibles: "
                + ", ".join(hojas)
            )

    except Exception as error:

        st.error(
            f"No fue posible conectar con el MRP: {error}"
        )


# =====================================================
# 7. PIE DE PÁGINA
# =====================================================

st.markdown("---")

st.caption(
    "ENAEX CHILE | REPORTE SEMANAL | PUNTA TEATINOS"
)


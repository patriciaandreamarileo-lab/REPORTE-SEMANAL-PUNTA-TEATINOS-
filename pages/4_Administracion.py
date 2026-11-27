
import streamlit as st
import pandas as pd

from io import BytesIO

from modules.github_storage import (
    subir_archivo_github,
    descargar_archivo_github
)


# =========================================================
# 1. CONFIGURACIÓN
# =========================================================

COLOR_AZUL = "#102F4A"
COLOR_AZUL_MEDIO = "#286B9E"

RUTA_MRP = "data/MRP/Planificacion_MRP.xlsm"

RUTA_CONSUMO = (
    "data/CONSUMO/consumo_punta_teatinos.xlsx"
)

RUTA_PRECIOS = (
    "data/PRECIOS/precios_punta_teatinos.xlsx"
)


# =========================================================
# 2. ESTILOS
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #F4F7FB;
}

.main .block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.admin-header {
    background: linear-gradient(
        110deg,
        #102F4A 0%,
        #286B9E 100%
    );
    padding: 28px 32px;
    border-radius: 15px;
    color: white;
    margin-bottom: 30px;
}

.admin-title {
    color: white;
    font-size: 29px;
    font-weight: 800;
}

.admin-subtitle {
    color: #E5EDF5;
    font-size: 15px;
    margin-top: 8px;
}

.section-description {
    color: #718096;
    font-size: 14px;
    margin-bottom: 18px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: white;
    border-radius: 12px;
    border-color: #D9E0E8;
}

div[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #DCE4EF;
    border-radius: 10px;
    padding: 15px;
}

.stButton > button {
    background-color: #102F4A;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #286B9E;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. ENCABEZADO
# =========================================================

st.markdown(
    '<div class="admin-header">'
    '<div class="admin-title">ADMINISTRACIÓN</div>'
    '<div class="admin-subtitle">'
    'ENAEX CHILE | Gestión y actualización de archivos '
    '| Punta Teatinos'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# 4. AUTENTICACIÓN
# =========================================================

if "admin_autorizado" not in st.session_state:
    st.session_state.admin_autorizado = False


if not st.session_state.admin_autorizado:

    st.subheader("Acceso de administrador")

    st.markdown(
        "Ingresa la contraseña para habilitar "
        "la carga y actualización de archivos."
    )

    clave = st.text_input(
        "Contraseña de administración",
        type="password",
        key="clave_administracion"
    )

    if st.button(
        "Ingresar",
        use_container_width=True
    ):

        try:

            clave_correcta = st.secrets["CLAVE_SUBIDA"]

        except Exception:

            st.error(
                "No se encontró CLAVE_SUBIDA en los secretos "
                "de Streamlit. Revisa la configuración."
            )

            st.stop()

        if clave == clave_correcta:

            st.session_state.admin_autorizado = True
            st.rerun()

        else:

            st.error(
                "La contraseña ingresada es incorrecta."
            )

    st.stop()


# =========================================================
# 5. SESIÓN AUTORIZADA
# =========================================================

col1, col2 = st.columns([4, 1])

with col1:

    st.success("Acceso autorizado.")

with col2:

    if st.button(
        "Cerrar sesión",
        use_container_width=True
    ):

        st.session_state.admin_autorizado = False
        st.rerun()


st.divider()


# =========================================================
# 6. FUNCIONES DE VALIDACIÓN
# =========================================================

def validar_mrp(archivo):

    contenido = archivo.getvalue()

    excel = pd.ExcelFile(
        BytesIO(contenido),
        engine="openpyxl"
    )

    if "NS" not in excel.sheet_names:

        raise ValueError(
            "El archivo MRP no contiene la hoja NS."
        )

    datos = pd.read_excel(
        BytesIO(contenido),
        sheet_name="NS",
        header=None,
        engine="openpyxl"
    )

    encabezados_encontrados = False

    for _, fila in datos.iterrows():

        valores = (
            fila.fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
            .tolist()
        )

        if (
            "CENTRO" in valores
            and "MATERIAL" in valores
        ):

            encabezados_encontrados = True
            break

    if not encabezados_encontrados:

        raise ValueError(
            "No se encontraron los encabezados "
            "Centro y Material en la hoja NS."
        )

    return True


def validar_consumo(archivo):

    excel = pd.ExcelFile(
        BytesIO(archivo.getvalue()),
        engine="openpyxl"
    )

    if "Data" not in excel.sheet_names:

        raise ValueError(
            "El archivo de consumo no contiene la hoja Data."
        )

    datos = pd.read_excel(
        BytesIO(archivo.getvalue()),
        sheet_name="Data",
        nrows=5,
        engine="openpyxl"
    )

    columnas_requeridas = [
        "Material",
        "Centro",
        "Clase de movimiento",
        "Ctd.en UM entrada",
        "Fecha contabiliz."
    ]

    faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in datos.columns
    ]

    if faltantes:

        raise ValueError(
            "Faltan columnas necesarias: "
            + ", ".join(faltantes)
        )

    return True


def validar_precios(archivo):

    excel = pd.ExcelFile(
        BytesIO(archivo.getvalue()),
        engine="openpyxl"
    )

    if "Data" not in excel.sheet_names:

        raise ValueError(
            "El archivo de precios no contiene la hoja Data."
        )

    datos = pd.read_excel(
        BytesIO(archivo.getvalue()),
        sheet_name="Data",
        nrows=5,
        engine="openpyxl"
    )

    columnas_requeridas = [
        "Material",
        "Centro",
        "Clase de movimiento",
        "Fecha contabiliz.",
        "Pedido",
        "Moneda",
        "Impte.mon.local",
        "Ctd.en UM entrada",
        "Un.medida de entrada"
    ]

    faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in datos.columns
    ]

    if faltantes:

        raise ValueError(
            "Faltan columnas necesarias: "
            + ", ".join(faltantes)
        )

    return True


# =========================================================
# 7. FUNCIÓN GENERAL DE CARGA
# =========================================================

def procesar_carga(
    archivo,
    ruta,
    funcion_validacion,
    nombre
):

    if archivo is None:

        st.warning(
            "Primero debes seleccionar un archivo."
        )

        return

    try:

        # Validar el archivo seleccionado
        funcion_validacion(archivo)

        # Obtener el contenido binario del archivo
        contenido = archivo.getvalue()

        if not isinstance(contenido, bytes):

            raise TypeError(
                "El contenido del archivo no está "
                "en formato binario."
            )

        # Subir a GitHub:
        # primero la ruta y después los bytes
        subir_archivo_github(
            ruta,
            contenido,
            mensaje=f"Actualización de {nombre} desde el dashboard"
        )

        st.success(
            f"{nombre} actualizado correctamente en GitHub."
        )

        # Limpiar datos almacenados en caché
        st.cache_data.clear()

    except Exception as error:

        st.error(
            f"No fue posible actualizar {nombre}: {error}"
        )


# =========================================================
# 8. ACTUALIZACIÓN DEL MRP
# =========================================================

st.subheader("Actualización del MRP")

st.markdown(
    '<div class="section-description">'
    'Carga la versión actualizada del archivo MRP '
    'utilizado por Punta Teatinos.'
    '</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    archivo_mrp = st.file_uploader(
        "Seleccionar archivo MRP",
        type=["xlsm"],
        key="subir_mrp_punta"
    )

    if archivo_mrp is not None:

        st.caption(
            f"Archivo seleccionado: {archivo_mrp.name}"
        )

        if st.button(
            "Actualizar MRP",
            use_container_width=True,
            key="boton_mrp_punta"
        ):

            procesar_carga(
                archivo_mrp,
                RUTA_MRP,
                validar_mrp,
                "El MRP"
            )


st.divider()


# =========================================================
# 9. ACTUALIZACIÓN DEL CONSUMO SAP
# =========================================================

st.subheader("Actualización del consumo mensual")

st.markdown(
    '<div class="section-description">'
    'Carga el archivo Excel exportado desde SAP '
    'con los movimientos de consumo de Punta Teatinos.'
    '</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    archivo_consumo = st.file_uploader(
        "Seleccionar archivo de consumo SAP",
        type=["xlsx"],
        key="subir_consumo_punta"
    )

    if archivo_consumo is not None:

        st.caption(
            f"Archivo seleccionado: {archivo_consumo.name}"
        )

        if st.button(
            "Actualizar consumo mensual",
            use_container_width=True,
            key="boton_consumo_punta"
        ):

            procesar_carga(
                archivo_consumo,
                RUTA_CONSUMO,
                validar_consumo,
                "El consumo mensual de Punta Teatinos"
            )


st.divider()


# =========================================================
# 10. ACTUALIZACIÓN DE PRECIOS
# =========================================================

st.subheader("Actualización de precios")

st.markdown(
    '<div class="section-description">'
    'Carga el archivo Excel con los movimientos de entrada '
    'de mercancías y precios de las materias primas '
    'de Punta Teatinos.'
    '</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    archivo_precios = st.file_uploader(
        "Seleccionar archivo de precios SAP",
        type=["xlsx"],
        key="subir_precios_punta"
    )

    if archivo_precios is not None:

        st.caption(
            f"Archivo seleccionado: {archivo_precios.name}"
        )

        if st.button(
            "Actualizar precios",
            use_container_width=True,
            key="boton_precios_punta"
        ):

            procesar_carga(
                archivo_precios,
                RUTA_PRECIOS,
                validar_precios,
                "Los precios de Punta Teatinos"
            )


st.divider()


# =========================================================
# 11. ESTADO DE ARCHIVOS EN GITHUB
# =========================================================

st.subheader("Archivos almacenados en GitHub")

archivos = [
    ("Archivo MRP", RUTA_MRP),
    ("Consumo SAP", RUTA_CONSUMO),
    ("Precios SAP", RUTA_PRECIOS)
]

if st.button(
    "Verificar archivos almacenados",
    use_container_width=True
):

    for nombre, ruta in archivos:

        try:

            contenido = descargar_archivo_github(ruta)

            if contenido is not None:

                st.success(
                    f"{nombre}: archivo disponible."
                )

            else:

                st.warning(
                    f"{nombre}: todavía no se ha cargado."
                )

        except Exception as error:

            st.warning(
                f"{nombre}: no se pudo verificar su disponibilidad. "
                f"Detalle: {error}"
            )


# =========================================================
# 12. PIE DE PÁGINA
# =========================================================

st.markdown("""
<div style="
    text-align:center;
    color:#8795A6;
    font-size:12px;
    margin-top:45px;
    padding:18px;
    border-top:1px solid #DCE4EF;
">
    ENAEX CHILE | ADMINISTRACIÓN | PUNTA TEATINOS
</div>
""", unsafe_allow_html=True)

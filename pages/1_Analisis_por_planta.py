import streamlit as st
import pandas as pd

from modules.mrp_reader import cargar_mrp


# =========================================================
# 1. CONFIGURACIÓN E IDENTIDAD VISUAL
# =========================================================

COLOR_AZUL = "#102F4A"
COLOR_AZUL_MEDIO = "#286B9E"
COLOR_FONDO = "#F4F7FB"
COLOR_BORDE = "#D9E0E8"

CENTRO = "E026"
PLANTA = "PUNTA TEATINOS"
UBICACION = "La Serena"


st.markdown("""
<style>

.stApp {
    background-color: #F4F7FB;
}

.main .block-container {
    max-width: 1500px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.plant-header {
    background: linear-gradient(
        110deg,
        #102F4A 0%,
        #286B9E 100%
    );
    padding: 30px;
    border-radius: 15px;
    color: white;
    margin-bottom: 35px;
}

.header-label {
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #DCEAF5;
}

.header-name {
    font-size: 30px;
    font-weight: 800;
    color: white;
    margin-top: 12px;
}

.header-description {
    font-size: 15px;
    color: #F0F5FA;
    margin-top: 12px;
}

.section-description {
    color: #7B8794;
    font-size: 13px;
    margin-bottom: 16px;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #DCE4EF;
    border-radius: 12px;
    padding: 18px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px;
    border-color: #D9E0E8;
}

.alert-title {
    color: #24364B;
    font-size: 21px;
    font-weight: 750;
}

.alert-description {
    color: #687E96;
    font-size: 14px;
}

.material-title {
    color: #173B5E;
    font-size: 21px;
    font-weight: 750;
}

.footer {
    text-align: center;
    color: #8492A6;
    font-size: 12px;
    margin-top: 45px;
    padding: 18px;
    border-top: 1px solid #DCE4EF;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 2. FUNCIONES AUXILIARES
# =========================================================

def formato_numero(valor, decimales=0):

    if pd.isna(valor):
        return "—"

    return (
        f"{valor:,.{decimales}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def convertir_numerico(df, columnas):

    for columna in columnas:

        if columna in df.columns:

            df[columna] = pd.to_numeric(
                df[columna],
                errors="coerce"
            )

    return df


def obtener_columna(df, posibles):

    for columna in posibles:

        if columna in df.columns:
            return columna

    return None


def obtener_activos(df):

    if "MMPP Activa" not in df.columns:
        return df.copy()

    activos = (
        df["MMPP Activa"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df[
        activos.isin(["SI", "SÍ"])
    ].copy()


def calcular_nivel_servicio(df):

    """
    Cálculo ponderado por Riesgo MMPP.

    EB = 100%
    SB = 50%
    BB = 0%
    """

    if df.empty or "Riesgo MMPP" not in df.columns:
        return None

    columna_ns = obtener_columna(
        df,
        ["NS", "NS Corregido"]
    )

    if columna_ns is None:
        return None

    riesgo = pd.to_numeric(
        df["Riesgo MMPP"],
        errors="coerce"
    ).fillna(0)

    clasificacion = (
        df[columna_ns]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    riesgo_eb = riesgo[clasificacion == "EB"].sum()
    riesgo_sb = riesgo[clasificacion == "SB"].sum()
    riesgo_bb = riesgo[clasificacion == "BB"].sum()

    total = riesgo_eb + riesgo_sb + riesgo_bb

    if total <= 0:
        return None

    return (
        (riesgo_eb + 0.5 * riesgo_sb)
        / total
    ) * 100


# =========================================================
# 3. CARGAR INFORMACIÓN DEL MRP DESDE GITHUB
# =========================================================

@st.cache_data(ttl=60)
def obtener_datos_mrp():

    datos, hojas = cargar_mrp()

    return datos, hojas


try:

    with st.spinner("Cargando información del MRP..."):

        datos_mrp, hojas_mrp = obtener_datos_mrp()

    if datos_mrp is None or datos_mrp.empty:

        st.error(
            "El archivo MRP no contiene registros "
            "o no fue posible obtener la información."
        )

        st.stop()

except Exception as error:

    st.error(
        f"No fue posible cargar el archivo MRP: {error}"
    )

    st.stop()


# =========================================================
# 4. LIMPIEZA Y PREPARACIÓN DE DATOS
# =========================================================

datos_mrp = datos_mrp.copy()

datos_mrp.columns = [
    str(columna).replace("\n", " ").strip()
    for columna in datos_mrp.columns
]

columnas_requeridas = [
    "Centro",
    "Material",
    "Descripción del material"
]

faltantes = [
    columna
    for columna in columnas_requeridas
    if columna not in datos_mrp.columns
]

if faltantes:

    st.error(
        "Faltan columnas necesarias en el MRP: "
        + ", ".join(faltantes)
    )

    st.stop()


# Limpiar centro

datos_mrp["Centro"] = (
    datos_mrp["Centro"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
    .str.replace(r"\.0$", "", regex=True)
)


# Limpiar código de material

datos_mrp["Material"] = (
    datos_mrp["Material"]
    .fillna("")
    .astype(str)
    .str.replace(r"\.0$", "", regex=True)
    .str.strip()
)


# Eliminar registros sin material o centro

datos_mrp = datos_mrp[
    (datos_mrp["Material"] != "")
    & (datos_mrp["Centro"] != "")
].copy()


# Convertir campos numéricos

columnas_numericas = [
    "Riesgo MMPP",
    "Consumo X̄",
    "Stock Actual",
    "Stock Óptimo",
    "Stock Seguridad",
    "Stock Máximo",
    "Cob. [Meses]",
    "Cobertura a [Días]",
    "Sobrestock [%]"
]

datos_mrp = convertir_numerico(
    datos_mrp,
    columnas_numericas
)


# Normalizar clasificación NS

for columna in ["NS", "NS Corregido"]:

    if columna in datos_mrp.columns:

        datos_mrp[columna] = (
            datos_mrp[columna]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )


# Obtener cobertura en días.
# Si el MRP solo tiene cobertura en meses,
# se convierte utilizando 30 días por mes.

if "Cobertura a [Días]" not in datos_mrp.columns:

    if "Cob. [Meses]" in datos_mrp.columns:

        datos_mrp["Cobertura a [Días]"] = (
            datos_mrp["Cob. [Meses]"] * 30
        )

    else:

        datos_mrp["Cobertura a [Días]"] = pd.NA


# =========================================================
# 5. FILTRAR PUNTA TEATINOS - CENTRO E026
# =========================================================

datos = datos_mrp[
    datos_mrp["Centro"] == CENTRO
].copy()


if datos.empty:

    st.warning(
        f"No se encontraron registros para {PLANTA} "
        f"(Centro {CENTRO}) en el archivo MRP."
    )

    st.subheader("Diagnóstico de centros")

    st.write(
        "Centros encontrados:",
        sorted(datos_mrp["Centro"].unique().tolist())
    )

    st.stop()


# =========================================================
# 6. DIAGNÓSTICO DE MATERIAS PRIMAS ACTIVAS
# =========================================================

st.subheader("Diagnóstico de datos MRP")

st.write(
    "Total de registros recibidos:",
    len(datos_mrp)
)

st.write(
    "Registros encontrados para E026:",
    len(datos)
)

st.write("Columnas disponibles:")

st.write(datos.columns.tolist())


if "MMPP Activa" in datos.columns:

    st.write("Valores encontrados en MMPP Activa:")

    st.dataframe(
        datos["MMPP Activa"]
        .value_counts(dropna=False)
        .rename_axis("Valor")
        .reset_index(name="Cantidad"),
        use_container_width=True,
        hide_index=True
    )

    st.write("Ejemplos de registros E026:")

    columnas_diagnostico = [
        columna
        for columna in [
            "Centro",
            "Material",
            "Descripción del material",
            "MMPP Activa"
        ]
        if columna in datos.columns
    ]

    st.dataframe(
        datos[columnas_diagnostico].head(15),
        use_container_width=True,
        hide_index=True
    )

else:

    st.error(
        "No existe la columna MMPP Activa "
        "en los datos recibidos."
    )

    st.write("Columnas disponibles:")
    st.write(datos.columns.tolist())

    st.stop()


# Aplicar filtro de materias primas activas

datos_activos = obtener_activos(datos)


st.write(
    "Materias primas activas reconocidas:",
    len(datos_activos)
)


if datos_activos.empty:

    st.warning(
        "El diagnóstico indica que no se reconocieron "
        "materias primas activas."
    )

    st.stop()


# =========================================================
# 7. ENCABEZADO DE LA PLANTA
# =========================================================

st.markdown("""
<div class="plant-header">

    <div class="header-label">
        ANÁLISIS INDIVIDUAL
    </div>

    <div class="header-name">
        PUNTA TEATINOS
    </div>

    <div class="header-description">
        La Serena | Enaex Chile | Centro E026
    </div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# 8. RESUMEN SUPERIOR
# =========================================================

col_grafico, col_resumen = st.columns(
    [1.05, 1],
    gap="large"
)


# ---------------------------------------------------------
# 8.1 DISTRIBUCIÓN DEL NIVEL DE SERVICIO
# ---------------------------------------------------------

with col_grafico:

    st.subheader("Distribución del nivel de servicio")

    columna_clasificacion = obtener_columna(
        datos_activos,
        ["NS Corregido", "NS"]
    )

    if columna_clasificacion:

        clasificaciones = (
            datos_activos[columna_clasificacion]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )

        conteo_ns = (
            clasificaciones[
                clasificaciones.isin(["EB", "SB", "BB"])
            ]
            .value_counts()
            .reindex(["EB", "SB", "BB"], fill_value=0)
        )

        datos_grafico = pd.DataFrame({
            "Clasificación": ["EB", "SB", "BB"],
            "Cantidad": [
                int(conteo_ns["EB"]),
                int(conteo_ns["SB"]),
                int(conteo_ns["BB"])
            ]
        })

        if datos_grafico["Cantidad"].sum() > 0:

            especificacion = {
                "mark": {
                    "type": "arc",
                    "innerRadius": 65,
                    "outerRadius": 125,
                    "stroke": "white",
                    "strokeWidth": 2
                },
                "encoding": {
                    "theta": {
                        "field": "Cantidad",
                        "type": "quantitative"
                    },
                    "color": {
                        "field": "Clasificación",
                        "type": "nominal",
                        "scale": {
                            "domain": ["EB", "SB", "BB"],
                            "range": [
                                "#16A34A",
                                "#3B82F6",
                                "#EF4444"
                            ]
                        },
                        "legend": {
                            "title": None,
                            "orient": "right"
                        }
                    },
                    "tooltip": [
                        {
                            "field": "Clasificación",
                            "type": "nominal"
                        },
                        {
                            "field": "Cantidad",
                            "type": "quantitative"
                        }
                    ]
                },
                "width": "container",
                "height": 310,
                "view": {
                    "stroke": None
                }
            }

            st.vega_lite_chart(
                datos_grafico,
                especificacion,
                use_container_width=True
            )

        else:

            st.info(
                "No hay clasificaciones EB, SB o BB disponibles."
            )

    else:

        st.warning(
            "No se encontró la columna de clasificación NS."
        )


# ---------------------------------------------------------
# 8.2 RESUMEN DE INVENTARIO
# ---------------------------------------------------------

with col_resumen:

    st.subheader("Resumen de inventario")

    cantidad_materiales = len(datos_activos)

    nivel_servicio = calcular_nivel_servicio(
        datos_activos
    )

    if "Cobertura a [Días]" in datos_activos.columns:

        materiales_bajo_10 = datos_activos[
            datos_activos["Cobertura a [Días]"] < 10
        ]

        cantidad_bajo_10 = len(materiales_bajo_10)

    else:

        cantidad_bajo_10 = 0

    with st.container(border=True):

        st.metric(
            "Materias primas",
            formato_numero(cantidad_materiales)
        )

    with st.container(border=True):

        st.metric(
            "Nivel de servicio",
            (
                f"{formato_numero(nivel_servicio, 1)}%"
                if nivel_servicio is not None
                else "—"
            )
        )

    with st.container(border=True):

        st.metric(
            "Materias con cobertura menor a 10 días",
            formato_numero(cantidad_bajo_10)
        )


st.divider()


# =========================================================
# 9. MATERIAS PRIMAS CON MENOR STOCK
# =========================================================

st.subheader("Materias primas con menor stock")

st.markdown(
    '<div class="section-description">'
    'Se muestran las cinco materias primas activas con menor '
    'cantidad disponible en stock actual.'
    '</div>',
    unsafe_allow_html=True
)


if "Stock Actual" in datos_activos.columns:

    tabla_stock = datos_activos.dropna(
        subset=["Stock Actual"]
    ).copy()

    tabla_stock = tabla_stock.sort_values(
        by="Stock Actual",
        ascending=True
    ).head(5)

    columnas_stock = [
        "Material",
        "Descripción del material",
        "UM",
        "Stock Actual",
        "Stock Seguridad",
        "Stock Óptimo",
        "Cobertura a [Días]"
    ]

    columnas_stock = [
        columna
        for columna in columnas_stock
        if columna in tabla_stock.columns
    ]

    if not tabla_stock.empty:

        tabla_mostrar = tabla_stock[columnas_stock].copy()

        st.dataframe(
            tabla_mostrar,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No hay información de stock disponible."
        )

else:

    st.warning(
        "El MRP no contiene la columna Stock Actual."
    )


st.divider()


# =========================================================
# 10. MATERIAS PRIMAS CON MENOR CONSUMO Y MAYOR COBERTURA
# =========================================================

st.subheader(
    "Materias primas con menor consumo y mayor cobertura"
)

st.markdown(
    '<div class="section-description">'
    'Se priorizan las materias primas con menor consumo promedio '
    'y, en caso de empate, mayor cobertura.'
    '</div>',
    unsafe_allow_html=True
)


if (
    "Consumo X̄" in datos_activos.columns
    and "Cobertura a [Días]" in datos_activos.columns
):

    tabla_consumo = datos_activos.dropna(
        subset=["Consumo X̄"]
    ).copy()

    tabla_consumo = tabla_consumo.sort_values(
        by=["Consumo X̄", "Cobertura a [Días]"],
        ascending=[True, False]
    ).head(5)

    tabla_consumo["Cob. [Meses]"] = (
        tabla_consumo["Cobertura a [Días]"] / 30
    )

    columnas_consumo = [
        "Material",
        "Descripción del material",
        "UM",
        "Consumo X̄",
        "Stock Actual",
        "Cobertura a [Días]",
        "Cob. [Meses]"
    ]

    columnas_consumo = [
        columna
        for columna in columnas_consumo
        if columna in tabla_consumo.columns
    ]

    if not tabla_consumo.empty:

        st.dataframe(
            tabla_consumo[columnas_consumo],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No hay información de consumo disponible."
        )

else:

    st.warning(
        "No se encontraron las columnas necesarias "
        "para realizar este análisis."
    )


st.divider()


# =========================================================
# 11. ALERTAS DE COBERTURA DE INVENTARIO
# =========================================================

st.subheader("Alertas de cobertura de inventario")

if "Cobertura a [Días]" in datos_activos.columns:

    alertas = datos_activos[
        datos_activos["Cobertura a [Días]"] < 10
    ].copy()

    alertas = alertas.sort_values(
        by="Cobertura a [Días]",
        ascending=True
    )

    if not alertas.empty:

        st.warning(
            f"⚠️ ¡ATENCIÓN! Se identificaron "
            f"{len(alertas)} materias primas con menos "
            f"de 10 días de cobertura."
        )

        for _, material in alertas.iterrows():

            codigo = str(material["Material"])

            descripcion = str(
                material["Descripción del material"]
            )

            cobertura = material.get(
                "Cobertura a [Días]"
            )

            stock = material.get(
                "Stock Actual"
            )

            consumo = material.get(
                "Consumo X̄"
            )

            comentario = material.get(
                "Comentario",
                material.get("Observaciones", "")
            )

            with st.container(border=True):

                st.markdown(
                    f"""
                    <div class="material-title">
                        🔴 Material {codigo}
                    </div>
                    <div style="margin-top:10px;">
                        {descripcion}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write("")

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Cobertura",
                    (
                        f"{formato_numero(cobertura, 2)} días"
                        if pd.notna(cobertura)
                        else "—"
                    )
                )

                c2.metric(
                    "Stock actual",
                    formato_numero(stock, 2)
                )

                c3.metric(
                    "Consumo promedio",
                    formato_numero(consumo, 2)
                )

                if (
                    pd.notna(comentario)
                    and str(comentario).strip()
                    and str(comentario).lower() != "nan"
                ):

                    st.caption(
                        f"Comentario: {comentario}"
                    )

    else:

        st.success(
            "No se identificaron materias primas "
            "con menos de 10 días de cobertura."
        )

else:

    st.warning(
        "No se encontró la columna de cobertura en el MRP."
    )


st.divider()


# =========================================================
# 12. CONSULTA INDIVIDUAL DE MATERIAS PRIMAS
# =========================================================

st.subheader(
    "Consulta individual de materias primas"
)

st.markdown(
    '<div class="section-description">'
    'Selecciona una materia prima para consultar sus indicadores '
    'de inventario, consumo y cobertura.'
    '</div>',
    unsafe_allow_html=True
)


catalogo = datos_activos.copy()

catalogo["Etiqueta"] = (
    catalogo["Material"].astype(str)
    + " — "
    + catalogo["Descripción del material"].fillna("").astype(str)
)

catalogo = catalogo.sort_values(
    by="Material"
)


if not catalogo.empty:

    seleccion = st.selectbox(
        "Selecciona una materia prima",
        options=catalogo["Etiqueta"].tolist(),
        index=None,
        placeholder="Buscar por código de material...",
        key="seleccion_material_punta_teatinos"
    )

    if seleccion:

        material_seleccionado = catalogo[
            catalogo["Etiqueta"] == seleccion
        ].iloc[0]

        st.write("")

        st.markdown(
            f"### {material_seleccionado['Descripción del material']}"
        )

        st.caption(
            f"Código de material: {material_seleccionado['Material']}"
        )

        # Primera fila de indicadores

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Consumo promedio",
            formato_numero(
                material_seleccionado.get("Consumo X̄"),
                2
            )
        )

        c2.metric(
            "Stock actual",
            formato_numero(
                material_seleccionado.get("Stock Actual"),
                2
            )
        )

        c3.metric(
            "Cobertura",
            (
                f"{formato_numero(material_seleccionado.get('Cobertura a [Días]'), 2)} días"
                if pd.notna(
                    material_seleccionado.get("Cobertura a [Días]")
                )
                else "—"
            )
        )

        # Segunda fila de indicadores

        c4, c5, c6 = st.columns(3)

        c4.metric(
            "Stock de seguridad",
            formato_numero(
                material_seleccionado.get("Stock Seguridad"),
                2
            )
        )

        c5.metric(
            "Stock óptimo",
            formato_numero(
                material_seleccionado.get("Stock Óptimo"),
                2
            )
        )

        c6.metric(
            "Stock máximo",
            formato_numero(
                material_seleccionado.get("Stock Máximo"),
                2
            )
        )

        # Clasificación y observaciones

        st.write("")

        c7, c8 = st.columns(2)

        c7.metric(
            "Nivel de servicio",
            str(material_seleccionado.get("NS", "—"))
        )

        c8.metric(
            "Nivel de servicio corregido",
            str(material_seleccionado.get("NS Corregido", "—"))
        )

        comentario = material_seleccionado.get(
            "Comentario",
            material_seleccionado.get("Observaciones", "")
        )

        if (
            pd.notna(comentario)
            and str(comentario).strip()
            and str(comentario).lower() != "nan"
        ):

            st.markdown("**Comentario del material**")

            st.info(str(comentario))

else:

    st.info(
        "No existen materias primas activas para consultar."
    )


# =========================================================
# 13. PIE DE PÁGINA
# =========================================================

st.markdown("""
<div class="footer">
    REPORTE SEMANAL PUNTA TEATINOS
    | ENAEX CHILE
</div>
""", unsafe_allow_html=True)

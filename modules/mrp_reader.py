
import pandas as pd
import streamlit as st

from io import BytesIO

from modules.github_storage import (
    descargar_archivo_github,
    RUTA_MRP
)


# =========================================================
# CONFIGURACIÓN
# =========================================================

CENTRO_PUNTA_TEATINOS = "E026"


# =========================================================
# LIMPIEZA DE DATOS
# =========================================================

def limpiar_codigo(valor):

    if pd.isna(valor):
        return ""

    codigo = str(valor).strip()

    if codigo.endswith(".0"):
        codigo = codigo[:-2]

    return codigo


def normalizar_texto(valor):

    if pd.isna(valor):
        return ""

    return (
        str(valor)
        .strip()
        .replace("\n", " ")
    )


# =========================================================
# DETECTAR FILA DE ENCABEZADOS
# =========================================================

def detectar_encabezado(datos):

    for indice, fila in datos.iterrows():

        valores = [
            normalizar_texto(valor).upper()
            for valor in fila.tolist()
        ]

        tiene_centro = "CENTRO" in valores
        tiene_material = "MATERIAL" in valores

        tiene_descripcion = any(
            "DESCRIPCIÓN DEL MATERIAL" in valor
            or "DESCRIPCION DEL MATERIAL" in valor
            for valor in valores
        )

        if (
            tiene_centro
            and tiene_material
            and tiene_descripcion
        ):

            return indice

    raise ValueError(
        "No se pudo encontrar la fila de encabezados. "
        "Se necesitan las columnas Centro, Material "
        "y Descripción del material."
    )


# =========================================================
# LEER UNA HOJA DEL MRP
# =========================================================

def leer_hoja_mrp(contenido, nombre_hoja):

    datos_originales = pd.read_excel(
        BytesIO(contenido),
        sheet_name=nombre_hoja,
        header=None,
        engine="openpyxl"
    )

    fila_encabezado = detectar_encabezado(
        datos_originales
    )

    encabezados = (
        datos_originales.iloc[fila_encabezado]
        .fillna("")
        .apply(normalizar_texto)
    )

    datos = datos_originales.iloc[
        fila_encabezado + 1:
    ].copy()

    datos.columns = encabezados

    datos = datos.loc[
        :,
        datos.columns != ""
    ]

    datos = datos.dropna(how="all")

    datos.columns = [
        normalizar_texto(columna)
        for columna in datos.columns
    ]

    return datos.reset_index(drop=True)


# =========================================================
# PREPARAR COLUMNAS
# =========================================================

def preparar_datos(datos):

    datos = datos.copy()

    # Limpiar centro
    if "Centro" in datos.columns:

        datos["Centro"] = (
            datos["Centro"]
            .astype(str)
            .str.strip()
        )

        datos["Centro"] = (
            datos["Centro"]
            .str.replace(r"\.0$", "", regex=True)
        )

    # Limpiar códigos de materiales
    if "Material" in datos.columns:

        datos["Material"] = (
            datos["Material"]
            .apply(limpiar_codigo)
        )

    # Limpiar columna Concat, si existe
    if "Concat" in datos.columns:

        datos["Concat"] = (
            datos["Concat"]
            .apply(limpiar_codigo)
        )

    return datos


# =========================================================
# CARGAR INFORMACIÓN MRP DESDE GITHUB
# =========================================================

@st.cache_data(ttl=60)
def cargar_mrp():

    contenido = descargar_archivo_github(
        RUTA_MRP
    )

    if contenido is None:

        raise FileNotFoundError(
            "No se encontró el archivo MRP en GitHub. "
            "Debes cargarlo desde Administración."
        )

    # Leer hojas
    ns = leer_hoja_mrp(
        contenido,
        "NS"
    )

    mrp = leer_hoja_mrp(
        contenido,
        "MRP"
    )

    # Preparar información
    ns = preparar_datos(ns)
    mrp = preparar_datos(mrp)

    # Filtrar Punta Teatinos
    ns = ns[
        ns["Centro"] == CENTRO_PUNTA_TEATINOS
    ].copy()

    mrp = mrp[
        mrp["Centro"] == CENTRO_PUNTA_TEATINOS
    ].copy()

    return (
        ns.reset_index(drop=True),
        mrp.reset_index(drop=True)
    )


# =========================================================
# OBTENER INFORMACIÓN DEL MRP
# =========================================================

def obtener_datos_mrp():

    try:

        ns, mrp = cargar_mrp()

        return {
            "ns": ns,
            "mrp": mrp,
            "error": None
        }

    except Exception as error:

        return {
            "ns": pd.DataFrame(),
            "mrp": pd.DataFrame(),
            "error": str(error)
        }

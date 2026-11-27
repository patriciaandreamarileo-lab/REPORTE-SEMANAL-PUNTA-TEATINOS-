
import re
import unicodedata
from io import BytesIO

import pandas as pd
import streamlit as st

from modules.github_storage import (
    descargar_archivo_github,
    RUTA_MRP
)


# =========================================================
# CONFIGURACIÓN
# =========================================================

CENTRO_PUNTA_TEATINOS = "E026"


# =========================================================
# NORMALIZACIÓN DE TEXTO
# =========================================================

def normalizar_texto(valor):

    if pd.isna(valor):
        return ""

    texto = str(valor).strip()
    texto = texto.replace("\n", " ")
    texto = texto.replace("\xa0", " ")

    texto = re.sub(r"\s+", " ", texto)

    return texto


def normalizar_nombre_columna(valor):

    texto = normalizar_texto(valor).upper()

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return texto.strip()


def normalizar_centro(valor):

    if pd.isna(valor):
        return ""

    centro = normalizar_texto(valor).upper()

    centro = centro.replace(" ", "")

    centro = re.sub(
        r"\.0$",
        "",
        centro
    )

    return centro


def limpiar_codigo(valor):

    if pd.isna(valor):
        return ""

    codigo = normalizar_texto(valor)

    codigo = re.sub(
        r"\.0$",
        "",
        codigo
    )

    return codigo


# =========================================================
# DETECTAR FILA DE ENCABEZADOS
# =========================================================

def detectar_encabezado(datos):

    for indice, fila in datos.iterrows():

        valores = [
            normalizar_nombre_columna(valor)
            for valor in fila.tolist()
        ]

        tiene_centro = any(
            valor == "CENTRO"
            for valor in valores
        )

        tiene_material = any(
            valor == "MATERIAL"
            for valor in valores
        )

        # No exigimos que exista una descripción.
        # Algunas hojas pueden tener encabezados distintos.

        if tiene_centro and tiene_material:

            return indice

    raise ValueError(
        "No se encontró una fila de encabezados "
        "que contenga las columnas Centro y Material."
    )


# =========================================================
# NORMALIZAR ENCABEZADOS
# =========================================================

def normalizar_encabezados(datos):

    equivalencias = {
        "CENTRO": "Centro",
        "MATERIAL": "Material",
        "DESCRIPCION DEL MATERIAL": "Descripción del material",
        "DESCRIPCION MATERIAL": "Descripción del material"
    }

    nuevas_columnas = []

    for columna in datos.columns:

        nombre = normalizar_texto(columna)

        nombre_normalizado = normalizar_nombre_columna(
            nombre
        )

        if nombre_normalizado in equivalencias:

            nombre = equivalencias[nombre_normalizado]

        nuevas_columnas.append(nombre)

    datos.columns = nuevas_columnas

    return datos


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

    # Eliminar columnas sin nombre
    datos = datos.loc[
        :,
        datos.columns != ""
    ]

    datos = datos.dropna(how="all")

    datos = normalizar_encabezados(datos)

    # Eliminar registros sin material
    if "Material" in datos.columns:

        datos["Material"] = (
            datos["Material"]
            .apply(limpiar_codigo)
        )

        datos = datos[
            datos["Material"] != ""
        ].copy()

    return datos.reset_index(drop=True)


# =========================================================
# PREPARAR DATOS
# =========================================================

def preparar_datos(datos):

    datos = datos.copy()

    datos = normalizar_encabezados(datos)

    if "Centro" not in datos.columns:

        raise ValueError(
            "La hoja no contiene una columna Centro."
        )

    if "Material" not in datos.columns:

        raise ValueError(
            "La hoja no contiene una columna Material."
        )

    datos["Centro"] = (
        datos["Centro"]
        .apply(normalizar_centro)
    )

    datos["Material"] = (
        datos["Material"]
        .apply(limpiar_codigo)
    )

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

    if not isinstance(contenido, bytes):

        raise TypeError(
            "El archivo MRP descargado no está "
            "en formato binario."
        )

    if not contenido:

        raise ValueError(
            "El archivo MRP descargado está vacío."
        )

    # Leer hojas originales
    ns = leer_hoja_mrp(
        contenido,
        "NS"
    )

    mrp = leer_hoja_mrp(
        contenido,
        "MRP"
    )

    # Preparar datos
    ns = preparar_datos(ns)
    mrp = preparar_datos(mrp)

    # Diagnóstico de centros disponibles
    centros_ns = sorted(
        ns["Centro"].dropna().unique().tolist()
    )

    centros_mrp = sorted(
        mrp["Centro"].dropna().unique().tolist()
    )

    # Filtrar Punta Teatinos
    ns_punta = ns[
        ns["Centro"] == CENTRO_PUNTA_TEATINOS
    ].copy()

    mrp_punta = mrp[
        mrp["Centro"] == CENTRO_PUNTA_TEATINOS
    ].copy()

    # Comprobar resultados
    if ns_punta.empty and mrp_punta.empty:

        raise ValueError(
            "No se encontraron registros del centro "
            f"{CENTRO_PUNTA_TEATINOS}.\n\n"
            f"Centros encontrados en hoja NS: {centros_ns}\n"
            f"Centros encontrados en hoja MRP: {centros_mrp}"
        )

    return (
        ns_punta.reset_index(drop=True),
        mrp_punta.reset_index(drop=True)
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

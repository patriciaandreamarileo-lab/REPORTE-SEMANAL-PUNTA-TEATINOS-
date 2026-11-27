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
# 1. CONFIGURACIÓN
# =========================================================

CENTRO_PUNTA_TEATINOS = "E026"


# =========================================================
# 2. NORMALIZACIÓN
# =========================================================

def normalizar_texto(valor):

    if pd.isna(valor):
        return ""

    texto = str(valor).strip()
    texto = texto.replace("\n", " ")
    texto = texto.replace("\xa0", " ")

    return re.sub(r"\s+", " ", texto)


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
# 3. DETECTAR ENCABEZADOS
# =========================================================

def detectar_encabezado(datos):

    for indice, fila in datos.iterrows():

        valores = [
            normalizar_nombre_columna(valor)
            for valor in fila.tolist()
        ]

        tiene_centro = "CENTRO" in valores
        tiene_material = "MATERIAL" in valores

        if tiene_centro and tiene_material:
            return indice

    raise ValueError(
        "No se encontró la fila de encabezados "
        "con las columnas Centro y Material."
    )


# =========================================================
# 4. NORMALIZAR NOMBRES DE COLUMNAS
# =========================================================

def normalizar_encabezados(datos):

    equivalencias = {
        "CENTRO": "Centro",
        "MATERIAL": "Material",
        "DESCRIPCION DEL MATERIAL": "Descripción del material",
        "UM": "UM",
        "UNIDAD DE MEDIDA": "UM",
        "MMPP ACTIVA": "MMPP Activa",
        "PRODUCTO": "Producto",
        "CONCAT": "Concat",
        "STOCK ACTUAL": "Stock Actual",
        "STOCK SEGURIDAD": "Stock Seguridad",
        "STOCK MAXIMO": "Stock Máximo",
        "STOCK OPTIMO": "Stock Óptimo",
        "CONSUMO PROYECTADO": "Consumo Proyectado",
        "CONSUMO X̄": "Consumo X̄",
        "RIESGO MMPP": "Riesgo MMPP",
        "RIESGO": "Riesgo",
        "NS": "NS",
        "NS CORREGIDO": "NS Corregido"
    }

    nuevas_columnas = []

    for columna in datos.columns:

        nombre = normalizar_texto(columna)

        clave = normalizar_nombre_columna(nombre)

        nombre_final = equivalencias.get(
            clave,
            nombre
        )

        nuevas_columnas.append(nombre_final)

    datos.columns = nuevas_columnas

    return datos


# =========================================================
# 5. LEER HOJA DEL EXCEL
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
        datos_originales
        .iloc[fila_encabezado]
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

    # Eliminar filas completamente vacías
    datos = datos.dropna(how="all")

    # Normalizar encabezados
    datos = normalizar_encabezados(datos)

    # Verificar columnas principales
    columnas_requeridas = [
        "Centro",
        "Material"
    ]

    faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in datos.columns
    ]

    if faltantes:

        raise ValueError(
            f"La hoja {nombre_hoja} no contiene: "
            + ", ".join(faltantes)
        )

    # Limpiar centro y material
    datos["Centro"] = (
        datos["Centro"]
        .apply(normalizar_centro)
    )

    datos["Material"] = (
        datos["Material"]
        .apply(limpiar_codigo)
    )

    # Eliminar filas sin identificación de material
    datos = datos[
        (datos["Centro"] != "")
        & (datos["Material"] != "")
    ].copy()

    return datos.reset_index(drop=True)


# =========================================================
# 6. UNIR NS Y MRP
# =========================================================

def unir_hojas(ns, mrp):

    claves = [
        "Centro",
        "Material"
    ]

    # Evitar que las columnas de identificación
    # se dupliquen durante la unión
    columnas_mrp = [
        columna
        for columna in mrp.columns
        if columna not in claves
    ]

    mrp_para_unir = mrp[
        claves + columnas_mrp
    ].copy()

    # Unir mediante centro y código de material
    # Se conserva toda la información de NS
    combinado = pd.merge(
        ns,
        mrp_para_unir,
        on=claves,
        how="left",
        suffixes=("", "_MRP"),
        sort=False
    )

    return combinado


# =========================================================
# 7. CARGAR MRP DESDE GITHUB
# =========================================================

@st.cache_data(ttl=60)
def cargar_mrp():

    contenido = descargar_archivo_github(
        RUTA_MRP
    )

    if contenido is None:

        raise FileNotFoundError(
            "No se encontró el archivo MRP en GitHub."
        )

    if not isinstance(contenido, bytes):

        raise TypeError(
            "El archivo MRP no se descargó en formato binario."
        )

    if not contenido:

        raise ValueError(
            "El archivo MRP está vacío."
        )

    # Leer las dos hojas
    ns = leer_hoja_mrp(
        contenido,
        "NS"
    )

    mrp = leer_hoja_mrp(
        contenido,
        "MRP"
    )

    # Comprobar centros disponibles
    centros_ns = sorted(
        ns["Centro"].unique().tolist()
    )

    centros_mrp = sorted(
        mrp["Centro"].unique().tolist()
    )

    # Comprobar registros de Punta Teatinos
    ns_punta = ns[
        ns["Centro"] == CENTRO_PUNTA_TEATINOS
    ].copy()

    mrp_punta = mrp[
        mrp["Centro"] == CENTRO_PUNTA_TEATINOS
    ].copy()

    if ns_punta.empty:

        raise ValueError(
            "No se encontraron registros E026 en NS. "
            f"Centros encontrados: {centros_ns}"
        )

    if mrp_punta.empty:

        raise ValueError(
            "No se encontraron registros E026 en MRP. "
            f"Centros encontrados: {centros_mrp}"
        )

    # Unir ambas hojas completas
    datos_combinados = unir_hojas(
        ns,
        mrp
    )

    # Información adicional para diagnóstico
    hojas = {
        "ns": ns,
        "mrp": mrp,
        "ns_punta": ns_punta,
        "mrp_punta": mrp_punta
    }

    return (
        datos_combinados.reset_index(drop=True),
        hojas
    )


# =========================================================
# 8. OBTENER INFORMACIÓN DEL MRP
# =========================================================

def obtener_datos_mrp():

    try:

        datos, hojas = cargar_mrp()

        return {
            "datos": datos,
            "hojas": hojas,
            "error": None
        }

    except Exception as error:

        return {
            "datos": pd.DataFrame(),
            "hojas": {},
            "error": str(error)
        }

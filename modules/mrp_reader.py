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
# 2. NORMALIZACIÓN DE TEXTO
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

    texto = texto.replace("̄", "")
    texto = texto.replace("Ø", "O")

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def normalizar_centro(valor):

    if pd.isna(valor):
        return ""

    centro = normalizar_texto(valor).upper()
    centro = centro.replace(" ", "")

    centro = re.sub(r"\.0$", "", centro)

    return centro


def limpiar_codigo(valor):

    if pd.isna(valor):
        return ""

    codigo = normalizar_texto(valor)

    codigo = re.sub(r"\.0$", "", codigo)

    return codigo


# =========================================================
# 3. DETECTAR FILA DE ENCABEZADOS
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

        if tiene_centro and tiene_material:

            return indice

    raise ValueError(
        "No se encontró la fila de encabezados "
        "con las columnas Centro y Material."
    )


# =========================================================
# 4. IDENTIFICAR Y NORMALIZAR COLUMNAS
# =========================================================

def identificar_nombre_columna(nombre):

    clave = normalizar_nombre_columna(nombre)

    # -----------------------------------------------------
    # Columnas generales
    # -----------------------------------------------------

    equivalencias = {

        "CENTRO": "Centro",

        "MATERIAL": "Material",

        "DESCRIPCION DEL MATERIAL":
            "Descripción del material",

        "DESCRIPCION MATERIAL":
            "Descripción del material",

        "UM": "UM",

        "UNIDAD DE MEDIDA": "UM",

        "MMPP ACTIVA": "MMPP Activa",

        "MMPP": "MMPP Activa",

        "PRODUCTO": "Producto",

        "CONCAT": "Concat",

        "STOCK ACTUAL": "Stock Actual",

        "STOCK SEGURIDAD": "Stock Seguridad",

        "STOCK MAXIMO": "Stock Máximo",

        "STOCK OPTIMO": "Stock Óptimo",

        "CONSUMO PROYECTADO": "Consumo Proyectado",

        "CONSUMO X": "Consumo X̄",

        "CONSUMO": "Consumo X̄",

        "RIESGO MMPP": "Riesgo MMPP",

        "RIESGO": "Riesgo",

        "NS": "NS",

        "NS CORREGIDO": "NS Corregido",

        "NS CORR": "NS Corregido",

        "COMENTARIO MMPP": "Comentario MMPP",

        "COMENTARIO": "Comentario"

    }

    if clave in equivalencias:

        return equivalencias[clave]

    # -----------------------------------------------------
    # Reconocimiento flexible de columnas
    # -----------------------------------------------------

    if clave.startswith("DESCRIPCION"):

        return "Descripción del material"

    if clave.startswith("STOCK ACTUAL"):

        return "Stock Actual"

    if clave.startswith("STOCK SEGURIDAD"):

        return "Stock Seguridad"

    if clave.startswith("STOCK MAXIMO"):

        return "Stock Máximo"

    if clave.startswith("STOCK OPTIMO"):

        return "Stock Óptimo"

    if clave.startswith("CONSUMO PROYECTADO"):

        return "Consumo Proyectado"

    if clave.startswith("CONSUMO"):

        return "Consumo X̄"

    if "RIESGO" in clave and "MMPP" in clave:

        return "Riesgo MMPP"

    if clave.startswith("RIESGO"):

        return "Riesgo"

    if clave.startswith("NS CORR"):

        return "NS Corregido"

    if clave.startswith("NS"):

        return "NS"

    if "COB" in clave and "DIA" in clave:

        return "Cobertura a [Días]"

    if "COB" in clave and (
        "MES" in clave
        or "MESES" in clave
    ):

        return "Cob. [Meses]"

    if "SOBRESTOCK" in clave:

        return "Sobrestock [%]"

    if "COMENTARIO" in clave:

        return "Comentario MMPP"

    return normalizar_texto(nombre)


def normalizar_encabezados(datos):

    nuevas_columnas = []

    for columna in datos.columns:

        nombre_final = identificar_nombre_columna(
            columna
        )

        nuevas_columnas.append(nombre_final)

    datos.columns = nuevas_columnas

    return datos


# =========================================================
# 5. LEER UNA HOJA DEL EXCEL
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

    # Comprobar columnas principales
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

    # Normalizar identificadores
    datos["Centro"] = (
        datos["Centro"]
        .apply(normalizar_centro)
    )

    datos["Material"] = (
        datos["Material"]
        .apply(limpiar_codigo)
    )

    # Eliminar registros sin identificación
    datos = datos[
        (datos["Centro"] != "")
        & (datos["Material"] != "")
    ].copy()

    return datos.reset_index(drop=True)


# =========================================================
# 6. UNIR HOJAS NS Y MRP
# =========================================================

def unir_hojas(ns, mrp):

    claves = [
        "Centro",
        "Material"
    ]

    # Evitar duplicación de identificadores
    columnas_mrp = [
        columna
        for columna in mrp.columns
        if columna not in claves
    ]

    mrp_para_unir = mrp[
        claves + columnas_mrp
    ].copy()

    # Evitar duplicaciones de registros en la unión.
    # Si existen varias filas por material en MRP,
    # se conserva la primera para evitar multiplicar filas.
    mrp_para_unir = mrp_para_unir.drop_duplicates(
        subset=claves,
        keep="first"
    )

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
# 7. VALIDAR COLUMNAS PARA EL DASHBOARD
# =========================================================

def validar_columnas_dashboard(datos):

    columnas_necesarias = [
        "Centro",
        "Material",
        "Descripción del material",
        "MMPP Activa",
        "NS",
        "NS Corregido",
        "Riesgo MMPP",
        "Consumo X̄",
        "Stock Actual",
        "Stock Óptimo",
        "Stock Seguridad",
        "Stock Máximo",
        "Cob. [Meses]",
        "Cobertura a [Días]"
    ]

    faltantes = [
        columna
        for columna in columnas_necesarias
        if columna not in datos.columns
    ]

    return faltantes


# =========================================================
# 8. CARGAR MRP DESDE GITHUB
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

    # -----------------------------------------------------
    # Leer las hojas
    # -----------------------------------------------------

    ns = leer_hoja_mrp(
        contenido,
        "NS"
    )

    mrp = leer_hoja_mrp(
        contenido,
        "MRP"
    )

    # -----------------------------------------------------
    # Identificar centros
    # -----------------------------------------------------

    centros_ns = sorted(
        ns["Centro"].unique().tolist()
    )

    centros_mrp = sorted(
        mrp["Centro"].unique().tolist()
    )

    # -----------------------------------------------------
    # Filtrar Punta Teatinos
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Unir las hojas
    # -----------------------------------------------------

    datos_combinados = unir_hojas(
        ns,
        mrp
    )

    # -----------------------------------------------------
    # Diagnóstico de columnas
    # -----------------------------------------------------

    faltantes = validar_columnas_dashboard(
        datos_combinados
    )

    # -----------------------------------------------------
    # Información adicional
    # -----------------------------------------------------

    hojas = {
        "ns": ns,
        "mrp": mrp,
        "ns_punta": ns_punta,
        "mrp_punta": mrp_punta,
        "columnas_ns": ns.columns.tolist(),
        "columnas_mrp": mrp.columns.tolist(),
        "columnas_combinadas": datos_combinados.columns.tolist(),
        "columnas_faltantes": faltantes
    }

    return (
        datos_combinados.reset_index(drop=True),
        hojas
    )


# =========================================================
# 9. OBTENER INFORMACIÓN DEL MRP
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

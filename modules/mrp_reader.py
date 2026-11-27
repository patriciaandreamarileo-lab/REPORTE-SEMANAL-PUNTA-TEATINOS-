import pandas as pd
import streamlit as st
import unicodedata

from io import BytesIO
from modules.github_storage import descargar_archivo_github


# =====================================================
# 1. CONFIGURACIÓN
# =====================================================

RUTA_MRP = "data/MRP/Planificacion_MRP.xlsm"

HOJA_PRINCIPAL = "NS"


# =====================================================
# 2. NORMALIZAR ENCABEZADOS
# =====================================================

def normalizar_texto(valor):

    texto = str(valor).strip().upper()

    texto = unicodedata.normalize(
        "NFKD",
        texto
    ).encode("ascii", "ignore").decode("ascii")

    return " ".join(texto.split())


# =====================================================
# 3. BUSCAR FILA DE ENCABEZADOS
# =====================================================

def buscar_encabezado(df_original):

    for i in range(len(df_original)):

        valores = [
            normalizar_texto(valor)
            for valor in df_original.iloc[i].tolist()
        ]

        tiene_centro = "CENTRO" in valores
        tiene_material = "MATERIAL" in valores

        tiene_descripcion = any(
            "DESCRIPCION DEL MATERIAL" in valor
            for valor in valores
        )

        if (
            tiene_centro
            and tiene_material
            and tiene_descripcion
        ):

            return i

    return None


# =====================================================
# 4. PREPARAR HOJA DEL MRP
# =====================================================

def preparar_hoja(excel, nombre_hoja):

    df_original = pd.read_excel(
        excel,
        sheet_name=nombre_hoja,
        header=None,
        engine="openpyxl"
    )

    fila_encabezado = buscar_encabezado(
        df_original
    )

    if fila_encabezado is None:

        return None

    encabezados = (
        df_original.iloc[fila_encabezado]
        .fillna("")
        .astype(str)
        .str.strip()
        .tolist()
    )

    # Evitar encabezados vacíos

    encabezados = [
        nombre if nombre else f"Columna_{i}"
        for i, nombre in enumerate(encabezados)
    ]

    # Evitar nombres duplicados

    usados = {}
    encabezados_finales = []

    for nombre in encabezados:

        if nombre in usados:

            usados[nombre] += 1

            encabezados_finales.append(
                f"{nombre}_{usados[nombre]}"
            )

        else:

            usados[nombre] = 0
            encabezados_finales.append(nombre)

    # Extraer registros posteriores al encabezado

    df = df_original.iloc[
        fila_encabezado + 1:
    ].copy()

    df.columns = encabezados_finales

    df = df.dropna(how="all")

    df = df.reset_index(drop=True)

    return df


# =====================================================
# 5. CARGAR MRP DESDE GITHUB
# =====================================================

@st.cache_data(ttl=60)
def cargar_mrp():

    # Descargar archivo

    contenido = descargar_archivo_github(
        RUTA_MRP
    )

    if contenido is None:

        raise FileNotFoundError(
            "No se encontró el archivo MRP en GitHub. "
            f"Ruta: {RUTA_MRP}"
        )

    # Abrir Excel

    archivo = BytesIO(contenido)

    excel = pd.ExcelFile(
        archivo,
        engine="openpyxl"
    )

    hojas = excel.sheet_names

    if not hojas:

        raise ValueError(
            "El archivo MRP no contiene hojas."
        )

    # Priorizar hoja NS

    if HOJA_PRINCIPAL in hojas:

        df = preparar_hoja(
            excel,
            HOJA_PRINCIPAL
        )

        if df is not None:

            return df, hojas

    # Si NS no tiene los encabezados esperados,
    # buscar automáticamente en las demás hojas.

    for nombre_hoja in hojas:

        if nombre_hoja == HOJA_PRINCIPAL:
            continue

        df = preparar_hoja(
            excel,
            nombre_hoja
        )

        if df is not None:

            return df, hojas

    raise ValueError(
        "No se encontraron los encabezados necesarios "
        "en ninguna hoja del MRP. Se requieren: "
        "Centro, Material y Descripción del material."
    )


# =====================================================
# 6. FUNCIÓN PARA LIMPIAR CÓDIGOS
# =====================================================

def limpiar_codigo(valor):

    if pd.isna(valor):
        return ""

    codigo = str(valor).strip()

    if codigo.endswith(".0"):
        codigo = codigo[:-2]

    return codigo


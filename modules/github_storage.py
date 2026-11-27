import streamlit as st
import requests
import base64


# =====================================================
# 1. CONFIGURACIÓN
# =====================================================

API_GITHUB = "https://api.github.com"


def obtener_configuracion():

    try:
        token = st.secrets["GITHUB_TOKEN"]
        repositorio = st.secrets["GITHUB_REPO"]

        rama = st.secrets.get(
            "GITHUB_BRANCH",
            "main"
        )

        if not token or not repositorio:
            raise ValueError("Configuración incompleta.")

        return {
            "token": token,
            "repositorio": repositorio,
            "rama": rama
        }

    except Exception as error:

        raise Exception(
            "No se encontró la configuración de GitHub "
            "en los Secrets de Streamlit."
        ) from error


# =====================================================
# 2. ENCABEZADOS DE CONEXIÓN
# =====================================================

def obtener_headers():

    config = obtener_configuracion()

    return {
        "Authorization": f"Bearer {config['token']}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }


# =====================================================
# 3. CONSTRUIR URL DEL ARCHIVO
# =====================================================

def construir_url(ruta):

    config = obtener_configuracion()

    ruta = str(ruta).replace("\\", "/").strip("/")

    return (
        f"{API_GITHUB}/repos/"
        f"{config['repositorio']}/contents/{ruta}"
    )


# =====================================================
# 4. DESCARGAR ARCHIVO DESDE GITHUB
# =====================================================

def descargar_archivo_github(ruta):

    config = obtener_configuracion()

    url = construir_url(ruta)

    parametros = {
        "ref": config["rama"]
    }

    respuesta = requests.get(
        url,
        headers=obtener_headers(),
        params=parametros,
        timeout=60
    )

    if respuesta.status_code == 404:
        return None

    if respuesta.status_code != 200:

        raise Exception(
            f"Error descargando archivo desde GitHub: "
            f"{respuesta.status_code} - {respuesta.text}"
        )

    datos = respuesta.json()

    contenido = datos.get("content", "")

    if not contenido:
        return None

    return base64.b64decode(contenido)


# =====================================================
# 5. SUBIR O ACTUALIZAR ARCHIVO EN GITHUB
# =====================================================

def subir_archivo_github(archivo, ruta):

    config = obtener_configuracion()

    url = construir_url(ruta)

    headers = obtener_headers()

    # Obtener contenido del archivo

    if hasattr(archivo, "getvalue"):

        contenido = archivo.getvalue()

    elif isinstance(archivo, bytes):

        contenido = archivo

    else:

        raise TypeError(
            "El archivo debe ser un archivo cargado "
            "desde Streamlit o contenido binario."
        )

    contenido_codificado = base64.b64encode(
        contenido
    ).decode("utf-8")

    # Comprobar si el archivo ya existe

    respuesta_actual = requests.get(
        url,
        headers=headers,
        params={"ref": config["rama"]},
        timeout=60
    )

    datos = {
        "message": f"Actualizar archivo {ruta}",
        "content": contenido_codificado,
        "branch": config["rama"]
    }

    # Si existe, obtener SHA para reemplazarlo

    if respuesta_actual.status_code == 200:

        datos["sha"] = respuesta_actual.json()["sha"]

    elif respuesta_actual.status_code != 404:

        raise Exception(
            "No se pudo comprobar el archivo en GitHub: "
            f"{respuesta_actual.status_code} - "
            f"{respuesta_actual.text}"
        )

    # Subir archivo

    respuesta = requests.put(
        url,
        headers=headers,
        json=datos,
        timeout=120
    )

    if respuesta.status_code not in (200, 201):

        raise Exception(
            "Error al guardar el archivo en GitHub: "
            f"{respuesta.status_code} - "
            f"{respuesta.text}"
        )

    return respuesta.json()


# =====================================================
# 6. VERIFICAR CONEXIÓN
# =====================================================

def verificar_conexion_github():

    config = obtener_configuracion()

    url = (
        f"{API_GITHUB}/repos/"
        f"{config['repositorio']}"
    )

    respuesta = requests.get(
        url,
        headers=obtener_headers(),
        timeout=30
    )

    if respuesta.status_code != 200:

        raise Exception(
            "No fue posible conectar con el repositorio: "
            f"{respuesta.status_code} - "
            f"{respuesta.text}"
        )

    return respuesta.json()


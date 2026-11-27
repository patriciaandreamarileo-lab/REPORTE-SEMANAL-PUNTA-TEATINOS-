
import base64
import requests
import streamlit as st


# =========================================================
# CONFIGURACIÓN
# =========================================================

def obtener_configuracion():
    """
    Obtiene las credenciales desde Streamlit Secrets.
    """

    try:
        token = st.secrets["GITHUB_TOKEN"]
        repositorio = st.secrets["GITHUB_REPO"]
        rama = st.secrets.get("GITHUB_BRANCH", "main")

        return token, repositorio, rama

    except Exception as error:
        raise ValueError(
            "Faltan configuraciones de GitHub en Streamlit Secrets. "
            "Verifica GITHUB_TOKEN y GITHUB_REPO."
        ) from error


def obtener_headers():
    token, _, _ = obtener_configuracion()

    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }


def construir_url(ruta):
    _, repositorio, _ = obtener_configuracion()

    return (
        f"https://api.github.com/repos/"
        f"{repositorio}/contents/{ruta}"
    )


# =========================================================
# DESCARGAR ARCHIVOS
# =========================================================

def descargar_archivo_github(ruta):
    """
    Descarga un archivo almacenado en el repositorio.
    Devuelve sus contenidos en bytes.
    """

    _, _, rama = obtener_configuracion()

    url = construir_url(ruta)

    parametros = {
        "ref": rama
    }

    respuesta = requests.get(
        url,
        headers=obtener_headers(),
        params=parametros,
        timeout=30
    )

    if respuesta.status_code == 404:
        return None

    if respuesta.status_code != 200:
        raise Exception(
            f"Error al descargar {ruta}: "
            f"{respuesta.status_code} - {respuesta.text}"
        )

    datos = respuesta.json()

    contenido = datos.get("content", "")
    contenido = contenido.replace("\n", "")

    return base64.b64decode(contenido)


# =========================================================
# SUBIR O ACTUALIZAR ARCHIVOS
# =========================================================

def subir_archivo_github(ruta, contenido, mensaje="Actualización desde dashboard"):
    """
    Sube un archivo nuevo o reemplaza uno existente.
    contenido debe ser de tipo bytes.
    """

    _, _, rama = obtener_configuracion()

    url = construir_url(ruta)

    headers = obtener_headers()

    # Consultar si el archivo ya existe para obtener su SHA
    respuesta_actual = requests.get(
        url,
        headers=headers,
        params={"ref": rama},
        timeout=30
    )

    sha = None

    if respuesta_actual.status_code == 200:
        sha = respuesta_actual.json().get("sha")

    elif respuesta_actual.status_code != 404:
        raise Exception(
            f"No se pudo verificar el archivo {ruta}: "
            f"{respuesta_actual.status_code} - {respuesta_actual.text}"
        )

    # Convertir el archivo a Base64
    contenido_base64 = base64.b64encode(contenido).decode("utf-8")

    datos = {
        "message": mensaje,
        "content": contenido_base64,
        "branch": rama
    }

    if sha:
        datos["sha"] = sha

    respuesta = requests.put(
        url,
        headers=headers,
        json=datos,
        timeout=60
    )

    if respuesta.status_code not in (200, 201):
        raise Exception(
            f"Error al guardar {ruta}: "
            f"{respuesta.status_code} - {respuesta.text}"
        )

    return True


# =========================================================
# VERIFICAR CONEXIÓN
# =========================================================

def verificar_conexion_github():
    """
    Comprueba que el token y el repositorio sean accesibles.
    """

    try:
        _, repositorio, _ = obtener_configuracion()

        url = f"https://api.github.com/repos/{repositorio}"

        respuesta = requests.get(
            url,
            headers=obtener_headers(),
            timeout=20
        )

        if respuesta.status_code == 200:
            return True, "Conexión con GitHub exitosa."

        return False, (
            f"No se pudo conectar con GitHub. "
            f"Código: {respuesta.status_code}. "
            f"Detalle: {respuesta.text}"
        )

    except Exception as error:
        return False, str(error)


# =========================================================
# RUTAS DE ARCHIVOS DE PUNTA TEATINOS
# =========================================================

RUTA_MRP = "data/MRP/Planificacion_MRP.xlsm"

RUTA_CONSUMO = (
    "data/CONSUMO/consumo_punta_teatinos.xlsx"
)

RUTA_PRECIOS = (
    "data/PRECIOS/precios_punta_teatinos.xlsx"
)

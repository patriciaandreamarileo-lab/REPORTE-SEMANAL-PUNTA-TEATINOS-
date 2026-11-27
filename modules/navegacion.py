import streamlit as st


# =====================================================
# 1. CONFIGURACIÓN DE NAVEGACIÓN
# =====================================================

def configurar_navegacion():

    paginas = {

        "GENERAL": [

            st.Page(
                "pages/0_Inicio.py",
                title="Inicio",
                icon="🏠",
                default=True
            )

        ],

        "ANÁLISIS": [

            st.Page(
                "pages/1_Analisis_por_planta.py",
                title="Análisis por planta",
                icon="🏭"
            ),

            st.Page(
                "pages/2_Consumo_promedio.py",
                title="Consumo promedio",
                icon="📊"
            ),

            st.Page(
                "pages/3_Evolucion_de_precios.py",
                title="Evolución de precios",
                icon="📈"
            )

        ],

        "ADMINISTRACIÓN": [

            st.Page(
                "pages/4_Administracion.py",
                title="Administración",
                icon="🔐"
            )

        ]

    }

    navegacion = st.navigation(
        paginas,
        position="sidebar"
    )

    navegacion.run()


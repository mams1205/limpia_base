import streamlit as st
import pandas as pd
from io import BytesIO
import re



st.title("Limpia base de datos")


# Cargar archivo
archivo = st.file_uploader(
    "Selecciona un archivo Excel",
    type=["xlsx", "xls"]
)

diccionario_df = pd.read_csv('diccionario.csv')

if archivo is not None:

    # Leer Excel
    df = pd.read_excel(archivo)

    st.success("Archivo cargado correctamente")
    st.subheader("Agregar nueva palabra a diccionario")
    palabra_incorrecta = st.text_input(
        "Palabra incorrecta"
    )

    palabra_correcta = st.text_input(
        "Reemplazar por"
    )
    
    if st.button("Agregar al diccionario"):

        if palabra_incorrecta and palabra_correcta:

            nueva_fila = pd.DataFrame({
                "incorrecta": [palabra_incorrecta],
                "correcta": [palabra_correcta]
            })

            diccionario_df = pd.concat(
                [diccionario_df, nueva_fila],
                ignore_index=True
            )

            # Guardar cambios
            diccionario_df.to_csv("diccionario.csv", index=False)

            st.success(
                f"Agregado: '{palabra_incorrecta}' → '{palabra_correcta}'"
            )

        st.dataframe(diccionario_df)

    diccionario = dict(
        zip(
            diccionario_df["incorrecta"],
            diccionario_df["correcta"]
        )
    )
    
    for columna in df.columns:

        if df[columna].dtype == "object":

            df[columna] = (
                df[columna]
                .astype(str)
                # espacios al inicio y final
                .str.strip()
                # múltiples espacios internos a uno solo
                .str.replace(r"\s+", " ", regex=True)
                # saltos de línea
                .str.replace("\n", " ", regex=False)
                .str.replace("\r", " ", regex=False)
                .str.replace(r"[^\w\sáéíóúÁÉÍÓÚñÑ.,;:/()-]", "", regex=True)
                .str.replace("\xa0", " ", regex=False)
                .str.upper()
            )


    # Mostrar columnas disponibles
    columnas = df.columns.tolist()

    columnas_seleccionadas = st.multiselect(
        "Selecciona las columnas a las que se aplicará el diccionario",
        columnas,
        default=columnas[:3] if len(columnas) >= 3 else columnas
    )
    
    
    

    if columnas_seleccionadas:

        df_filtrado = df[columnas_seleccionadas].copy()

        for columna in columnas_seleccionadas:

            df_filtrado[columna] = df_filtrado[columna].astype(str)

            for incorrecta, correcta in diccionario.items():
                df_filtrado[columna] = (
                    df_filtrado[columna]
                    .str.replace(
                        rf"\b{re.escape(incorrecta)}\b",
                        correcta,
                        case=False,
                        regex=True
                    )
                )

        # Reemplazar columnas corregidas en el original
        df[columnas_seleccionadas] = df_filtrado[columnas_seleccionadas]


    # Descargar resultado
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Datos"
        )

    excel = output.getvalue()

    st.download_button(
        label="Descargar Excel",
        data=excel,
        file_name="base_limpia",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
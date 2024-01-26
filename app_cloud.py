import streamlit as st
import pandas as pd
import pymssql
import requests
import base64
import zipfile
import xml.etree.ElementTree as ET
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
from streamlit.components.v1 import html
from datetime import datetime
import os
from sql_func import *
from dotenv import load_dotenv
load_dotenv()


st.set_page_config(page_title="App Template", layout="wide", initial_sidebar_state="expanded")

def load_lottieurl(url: str):
    r = requests.get(url)
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

loti1 = 'https://lottie.host/f6f6e864-5d1a-40a6-b1a2-ad7b010d8a42/Ciq4KXOz6S.json'
lot1 = load_lottieurl(loti1)
loti2= "https://lottie.host/fc7a5741-62bc-4f72-925f-98b938c1456e/rjLO4dpxBa.json"
lot2= load_lottieurl(loti2)


# Función para borrar un archivo si existe
def delete_file_if_exists(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
        return f"Archivo '{file_name}' eliminado."
    else:
        return f"Archivo '{file_name}' no existe."

def get_binary_file_downloader_html(file_path, file_label):
    with open(file_path, "rb") as file:
        bytes_data = file.read()
        b64 = base64.b64encode(bytes_data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_path}">Descargar {file_label}</a>'
        return href



def main():
    col1 = st.sidebar
    col2, col3 = st.columns((4, 1))


    with col1:      
        #st_lottie(lot2, key="lol",height=180, width=280)      
        with st.sidebar:
            st.image("banner-preview.png", width=300)
            selected = option_menu("Main Menu", ["Home", 'Traer transacciones', 'Configurar XML', 'Generar XML'],
                               icons=['house', 'bi bi-upload', 'bi bi-download'],
                               menu_icon="cast", default_index=0)

        add_vertical_space(3)
        st.write('Made with ❤️ by [Criss](https://github.com/cristian-data-science)')

    #col2.title("XML Gen")
    #col2.markdown("""
    #Generación de XML en base a folios entregados.
    #""")

    if selected == "Home":
        show_home(col1, col2)
    elif selected == "Traer transacciones":
        traer_trans(col2, "Traer transacciones")
    elif selected == "Configurar XML":
        config_xml(col2, "Configurar XML")
    elif selected == "Generar XML":
        gen_xml(col2, "Generar XML")

def ui_home(col, titulo, lottie_animacion, altura=700, ancho=780, espacios=4):
    espacio = "<br>" * espacios
    col.markdown(espacio, unsafe_allow_html=True)
    col.title(titulo)
    
    #st_lottie(lottie_animacion, key="loti1", height=altura, width=ancho)

def show_home(col1, col2):
    with col2:  
        #st.image("banner-preview.png",width=180)
        ui_home(col2, "Generación de XML en base a folios cargados", lot1)
        st_lottie(lot1, key="loti1", height=700, width=780)
        if st.button('Borrar Archivos'):
            #message_folios = delete_file_if_exists('folios.xlsx')
            message_lineasxml = delete_file_if_exists('lineasxml.xlsx')
            message_lineaseditadas = delete_file_if_exists('lineaseditadas.xlsx')

            # Mostrar mensajes
            #st.success(message_folios)
            st.success(message_lineasxml)
            st.success(message_lineaseditadas)


def traer_trans(col2, page_name):
    with col2:
        ui_home(col2, "Generación de XML en base a folios", lot1)

        
        uploaded_file = st.file_uploader("Subir Excel con folios", type=['xlsx'])

        if uploaded_file is not None:
            # Leer el archivo Excel
            df = pd.read_excel(uploaded_file)
            df['invoiceid'] = df['tipo_doc'].astype(str) + '-' + df['folios'].astype(str)
            #df

            # Asegurarse de que el archivo tiene el formato esperado
            if 'folios' in df.columns:
                # Convertir la columna de folios en una lista
                lista_folios = df['folios'].tolist()
                st.write("Folios cargados:")
                # Mostrar información sobre la cantidad de folios cargados
                st.info(f"Se han cargado {len(lista_folios)} folios.")
                st.header("Confección de lineas de factura")
                
                col1, col2 = st.columns(2)
                with col1:
                    fecha_desde = st.date_input("Fecha Desde", value=datetime(2023, 11, 1), min_value=datetime(2023, 11, 1))
                with col2:
                    fecha_hasta = st.date_input("Fecha Hasta", value=datetime.today())

                if st.button("Obtener Datos"):
                    with st.spinner('Cargando datos...'):
                        # Convertir las fechas a string si es necesario
                        fecha_desde_str = fecha_desde.strftime('%Y-%m-%d')
                        fecha_hasta_str = fecha_hasta.strftime('%Y-%m-%d')

                        # Llamada a la función obtener_lineas_xml
                        df_xml_invoice = obtener_lineas_xml(fecha_desde_str, fecha_hasta_str)

                        df_filtered = df_xml_invoice[df_xml_invoice['invoiceid'].isin(df['invoiceid'])]

                        # Mostrar el DataFrame filtrado
                        st.write(df_filtered)

                        # Guardar el DataFrame en un archivo Excel
                        df_filtered.to_excel("lineasxml.xlsx")
                        num_coincidencias = len(df_filtered)

                    st.success(f' {num_coincidencias} líneas hicieron coincidencia en el rango de fechas seleccionado.')

            else:
                st.error("El archivo no tiene el formato correcto. Asegúrate de que haya una columna titulada 'folios'.")

def config_xml(col2, page_name):
    with col2:
        ui_home(col2, "Generación de XML en base a folios", lot1)
        st.write("Párametros por defecto")
        

        def create_input_field(column, label, default_value):
            return column.text_input(label, value=default_value)
        with st.form(key='my_form'):
            col1, col2, col3, col4 = st.columns(4)
            tipo_doc = col1.selectbox('TipoDTE', ['61', '39', '33'], index=0)
            rut_emisor = create_input_field(col2, 'RUTEmisor', '76018478-0')
            razon_soc = create_input_field(col3, 'RznSoc', 'Patagonia Chile Limitada')
            giro_emisor = create_input_field(col4, 'GiroEmis', 'VENTA AL POR MAYOR DE OTROS PRODUCTOS N.')

            col5, col6, col7, col8 = st.columns(4)
            acteco = create_input_field(col5, 'Acteco', '519000')
            dir_origen = create_input_field(col6, 'DirOrigen', 'Los Conquistadores 2134')
            comuna_origen = create_input_field(col7, 'CmnaOrigen', 'Providencia')
            ciudad_origen = create_input_field(col8, 'CiudadOrigen', 'Santiago')
            submit_button = st.form_submit_button(label='Guardar Datos')

        
        df_default_data = pd.DataFrame({'TipoDTE': tipo_doc, 'RUTEmisor': rut_emisor, 'RznSoc': razon_soc, 'GiroEmis': giro_emisor, 'Acteco': acteco, 'DirOrigen': dir_origen, 'CmnaOrigen': comuna_origen, 'CiudadOrigen': ciudad_origen}, index=[0])   
       
        
        try:
            # Intenta leer el archivo Excel
            df_lineasxml = pd.read_excel("lineasxml.xlsx")
            # Si se carga correctamente, muestra el DataFrame
            #df_lineasxml
            # Iterar sobre las columnas de df_default_data
            for column in df_default_data.columns:
                # Si la columna existe en df_lineasxml, actualízala
                if column in df_lineasxml.columns:
                    df_lineasxml[column] = df_default_data.at[0, column]

            # Mostrar el DataFrame actualizado
            # borrar columna Unnamed: 0
            df_lineasxml = df_lineasxml.drop(columns=['Unnamed: 0'])

            # Excluir la columna 'CorreoRecep' temporalmente y verificar si todas las demás celdas en una fila tienen datos
            df_lineasxml['Datos_OK'] = df_lineasxml.drop(columns=['CorreoRecep']).notna().all(axis=1)

            # Mover la columna 'check' al principio del DataFrame
            cols = ['Datos_OK'] + [col for col in df_lineasxml if col != 'Datos_OK']
            df_lineasxml = df_lineasxml[cols]

            # Establecer la columna 'check' como índice del DataFrame
            df_lineasxml.set_index('Datos_OK', inplace=True)

            ###

            # Inicializar el estado de la sesión si es necesario
            if 'df_editable' not in st.session_state:
                st.session_state.df_editable = df_lineasxml.copy()

            # Mostrar el DataFrame editable
            edited_df = st.data_editor(st.session_state.df_editable, num_rows="dynamic")

            # Actualizar el DataFrame en el estado de la sesión
            st.session_state.df_editable = edited_df

            # Botón para guardar los cambios en un archivo
            if st.button('Guardar Cambios'):
                st.session_state.df_editable.to_excel("lineaseditadas.xlsx")
                st.success("Cambios guardados")





        except FileNotFoundError:
            # Si el archivo no se encuentra, muestra un mensaje informativo
            st.info("Aún no se han cargado folios a la app.")

def gen_xml(col2, page_name):
    with col2:
        ui_home(col2, "Generación de XML en base a folios", lot1)

        try:
            # Intenta leer el archivo Excel
            df_lineasxml = pd.read_excel("lineaseditadas.xlsx")
            # Si se carga correctamente, muestra el DataFrame
            st.write(df_lineasxml)
            comenzar_button = st.button('Comenzar creación de XMLs')
            if comenzar_button:
                st.write('La creación de XMLs ha comenzado...')

            # Iterar sobre cada fila del DataFrame y crear un archivo XML
            for index, row in df_lineasxml.iterrows():
                xml_tree = crear_xml(row)
                # Usar TipoDTE y Folio para el nombre del archivo
                nombre_archivo = f"{row['TipoDTE']}-{row['Folio']}.xml"
                xml_tree.write(nombre_archivo, encoding='utf-8', xml_declaration=True)
            
            # success message contando cuantos xml se crearon con la funcion crear_xml
            st.success(f"Se han creado {len(df_lineasxml)} archivos XML.")

            # comprimimr todos los xml creados en un zip
            st.write('Comprimiendo XMLs...')
            
            st.write('Comprimiendo XMLs...')
            with zipfile.ZipFile('xmls.zip', 'w') as zip:
                for file in os.listdir():
                    if file.endswith('.xml'):
                        zip.write(file)

            # Crear botón para descargar zip
            st.write('Descargar XMLs')
            st.markdown(get_binary_file_downloader_html('xmls.zip', 'XMLs'), unsafe_allow_html=True)

            # Borrar archivos xml
            message_xmls = delete_file_if_exists('xmls.zip')
        



        except FileNotFoundError:
            # Si el archivo no se encuentra, muestra un mensaje informativo
            st.info("Aún no se han cargado folios a la app.")

        

        
        

if __name__ == "__main__":
    main()

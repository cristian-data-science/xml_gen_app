import pymssql
import datetime
import os
from dotenv import load_dotenv
import pandas as pd
import xml.etree.ElementTree as ET
load_dotenv()  
import streamlit as st

def obtener_lineas_xml(fecha_desde, fecha_final):
    server = st.secrets["SERVER"]
    username = st.secrets["USER"]
    password = st.secrets["PASSWORD"]
    database = st.secrets["DATABASE"]

    conn = pymssql.connect(server, username, password, database)
    cursor = conn.cursor(as_dict=True)

    query = """
    SELECT DISTINCT * FROM XML_INVOICE WHERE FcheMIS BETWEEN %s AND %s
    """
    cursor.execute(query, (fecha_desde, fecha_final))
    df_xml_invoice = pd.DataFrame(cursor.fetchall())

    conn.close()
    return df_xml_invoice

def truncate_text(text):
    return str(text)[:40] 

def crear_xml(row):
    root = ET.Element("DTE")
    documento = ET.SubElement(root, "Documento")
    encabezado = ET.SubElement(documento, "Encabezado")

# Sección IdDoc
    id_doc = ET.SubElement(encabezado, "IdDoc")
    ET.SubElement(id_doc, "TipoDTE").text = truncate_text(row['TipoDTE'])
    ET.SubElement(id_doc, "Folio").text = truncate_text(row['Folio'])
    ET.SubElement(id_doc, "FchEmis").text = truncate_text(row['FchEmis'])
    ET.SubElement(id_doc, "FmaPago").text = truncate_text(row['FmaPago'])
    ET.SubElement(id_doc, "FchVenc").text = truncate_text(row['FchVenc'])

    # Sección Emisor
    emisor = ET.SubElement(encabezado, "Emisor")
    ET.SubElement(emisor, "RUTEmisor").text = truncate_text(row['RUTEmisor'])
    ET.SubElement(emisor, "RznSoc").text = truncate_text(row['RznSoc'])
    ET.SubElement(emisor, "GiroEmis").text = truncate_text(row['GiroEmis'])
    ET.SubElement(emisor, "Acteco").text = truncate_text(row['Acteco'])
    ET.SubElement(emisor, "DirOrigen").text = truncate_text(row['DirOrigen'])
    ET.SubElement(emisor, "CmnaOrigen").text = truncate_text(row['CmnaOrigen'])
    ET.SubElement(emisor, "CiudadOrigen").text = truncate_text(row['CiudadOrigen'])

    # Sección Receptor
    receptor = ET.SubElement(encabezado, "Receptor")
    ET.SubElement(receptor, "RUTRecep").text = truncate_text(row['RUTRecep'])
    ET.SubElement(receptor, "RznSocRecep").text = truncate_text(row['RznSocRecep'])
    ET.SubElement(receptor, "GiroRecep").text = truncate_text(row['GiroRecep'])
    ET.SubElement(receptor, "DirRecep").text = truncate_text(row['DirRecep'], 20)  
    ET.SubElement(receptor, "CmnaRecep").text = truncate_text(row['CmnaRecep'], 20) 
    ET.SubElement(receptor, "CiudadRecep").text = truncate_text(row['CiudadRecep'], 20)
    ET.SubElement(receptor, "CorreoRecep").text = truncate_text(row['CorreoRecep'])
    ET.SubElement(receptor, "Contacto").text = truncate_text(row['Contacto'])
    ET.SubElement(receptor, "CmnaPostal").text = truncate_text(row['CmnaPostal'])

    # Sección Totales
    totales = ET.SubElement(encabezado, "Totales")
    ET.SubElement(totales, "MntNeto").text = str(row['MntNeto'])
    ET.SubElement(totales, "TasaIVA").text = str(row['TasaIVA'])
    ET.SubElement(totales, "IVA").text = str(row['IVA'])
    ET.SubElement(totales, "MntTotal").text = str(row['MntTotal'])

    # Sección Detalle (modificada para manejar múltiples productos)
    detalles_fields = ['NroLinDet', 'TpoCodigo', 'VlrCodigo', 'NmbItem', 'QtyItem', 'UnmdItem', 'PrcItem', 'MontoItem']
    detalles_data = {field: str(row[field]).split(';') for field in detalles_fields}
    num_detalles = len(detalles_data['NroLinDet'])


    for i in range(num_detalles):
        detalle = ET.SubElement(documento, "Detalle")
        ET.SubElement(detalle, "NroLinDet").text = str(abs(int(float(detalles_data['NroLinDet'][i]))))
        cdg_item = ET.SubElement(detalle, "CdgItem")
        ET.SubElement(cdg_item, "TpoCodigo").text = str(detalles_data['TpoCodigo'][i])
        ET.SubElement(cdg_item, "VlrCodigo").text = str(detalles_data['VlrCodigo'][i])
        ET.SubElement(detalle, "NmbItem").text = str(detalles_data['NmbItem'][i])
        ET.SubElement(detalle, "QtyItem").text = str(abs(int(float(detalles_data['QtyItem'][i]))))
        ET.SubElement(detalle, "UnmdItem").text = str(detalles_data['UnmdItem'][i])
        ET.SubElement(detalle, "PrcItem").text = str(abs(int(float(detalles_data['PrcItem'][i]))))
        ET.SubElement(detalle, "MontoItem").text = str(abs(int(float(detalles_data['MontoItem'][i]))))


    # Sección Referencia
    referencia = ET.SubElement(documento, "Referencia")
    ET.SubElement(referencia, "NroLinRef").text = str((int(((row['NroLinRef'])))))
    #ET.SubElement(referencia, "TpoDocRef").text = str((int(((row['TpoDocRef'])))))
    ET.SubElement(referencia, "TpoDocRef").text = str(row['FolioRef']).split('-')[0] if '-' in str(row['FolioRef']) else str(row['FolioRef'])
    ET.SubElement(referencia, "FolioRef").text = str(row['FolioRef'])
    ET.SubElement(referencia, "FchRef").text = str(row['FchRef'])
    ET.SubElement(referencia, "CodRef").text = str(row['CodRef'])
    ET.SubElement(referencia, "RazonRef").text = str(row['RazonRef'])

    # Timestamp de firma (opcional)
    #ET.SubElement(documento, "TmstFirma").text = str(row['TmstFirma'])

  
    formatted_time = row['TmstFirma'].isoformat()

    # Create the XML element with the formatted time
    ET.SubElement(documento, "TmstFirma").text = formatted_time

    # Sección Personalizados (opcional)
    personalizados = ET.SubElement(documento, "Personalizados")
    ET.SubElement(personalizados, "contactos")
    ET.SubElement(personalizados, "impresora")

    # Genera el árbol XML
    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    return tree



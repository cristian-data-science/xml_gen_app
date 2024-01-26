import pymssql
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

def crear_xml(row):
    root = ET.Element("DTE")
    documento = ET.SubElement(root, "Documento")
    encabezado = ET.SubElement(documento, "Encabezado")

    # Sección IdDoc
    id_doc = ET.SubElement(encabezado, "IdDoc")
    ET.SubElement(id_doc, "TipoDTE").text = str(row['TipoDTE'])
    ET.SubElement(id_doc, "Folio").text = str(row['Folio'])
    ET.SubElement(id_doc, "FchEmis").text = str(row['FchEmis'])
    ET.SubElement(id_doc, "FmaPago").text = str(row['FmaPago'])
    ET.SubElement(id_doc, "FchVenc").text = str(row['FchVenc'])

    # Sección Emisor
    emisor = ET.SubElement(encabezado, "Emisor")
    ET.SubElement(emisor, "RUTEmisor").text = str(row['RUTEmisor'])
    ET.SubElement(emisor, "RznSoc").text = str(row['RznSoc'])
    ET.SubElement(emisor, "GiroEmis").text = str(row['GiroEmis'])
    ET.SubElement(emisor, "Acteco").text = str(row['Acteco'])
    ET.SubElement(emisor, "DirOrigen").text = str(row['DirOrigen'])
    ET.SubElement(emisor, "CmnaOrigen").text = str(row['CmnaOrigen'])
    ET.SubElement(emisor, "CiudadOrigen").text = str(row['CiudadOrigen'])

    # Sección Receptor
    receptor = ET.SubElement(encabezado, "Receptor")
    ET.SubElement(receptor, "RUTRecep").text = str(row['RUTRecep'])
    ET.SubElement(receptor, "RznSocRecep").text = str(row['RznSocRecep'])
    ET.SubElement(receptor, "GiroRecep").text = str(row['GiroRecep'])
    ET.SubElement(receptor, "DirRecep").text = str(row['DirRecep'])
    ET.SubElement(receptor, "CmnaRecep").text = str(row['CmnaRecep'])
    ET.SubElement(receptor, "CiudadRecep").text = str(row['CiudadRecep'])
    ET.SubElement(receptor, "CorreoRecep").text = str(row['CorreoRecep'])
    ET.SubElement(receptor, "Contacto").text = str(row['Contacto'])
    ET.SubElement(receptor, "CmnaPostal").text = str(row['CmnaPostal'])

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

    import xml.etree.ElementTree as ET

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
    ET.SubElement(referencia, "NroLinRef").text = str(row['NroLinRef'])
    ET.SubElement(referencia, "TpoDocRef").text = str(row['TpoDocRef'])
    ET.SubElement(referencia, "FolioRef").text = str(row['FolioRef'])
    ET.SubElement(referencia, "FchRef").text = str(row['FchRef'])
    ET.SubElement(referencia, "CodRef").text = str(row['CodRef'])
    ET.SubElement(referencia, "RazonRef").text = str(row['RazonRef'])

    # Timestamp de firma (opcional)
    #ET.SubElement(documento, "TmstFirma").text = str(row['TmstFirma'])

    # Sección Personalizados (opcional)
    personalizados = ET.SubElement(documento, "Personalizados")
    ET.SubElement(personalizados, "contactos")
    ET.SubElement(personalizados, "impresora")

    # Genera el árbol XML
    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    return tree



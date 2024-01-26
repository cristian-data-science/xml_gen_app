import pymssql
import os
from dotenv import load_dotenv
import pandas as pd
load_dotenv()  

def obtener_lineas_xml(fecha_desde, fecha_final):
    server = os.getenv('SERVER')
    username = os.getenv('USER')
    password = os.getenv('PASSWORD')
    database = os.getenv('DATABASE')

    conn = pymssql.connect(server, username, password, database)
    cursor = conn.cursor(as_dict=True)

    query = """
    SELECT * FROM XML_INVOICE WHERE FcheMIS BETWEEN %s AND %s
    """
    cursor.execute(query, (fecha_desde, fecha_final))
    df_xml_invoice = pd.DataFrame(cursor.fetchall())

    conn.close()
    return df_xml_invoice
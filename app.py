import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template, url_for
import pickle
from sklearn import svm
import sys
import logging
import os
from typing import Union
from google.cloud import storage
from io import StringIO
import altair as alt
import openpyxl


#-------------------------------------------------------IAP GCP
app = Flask(__name__)

#----------------------------------------------------B
# Configure this environment variable via app.yaml
#CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']

@app.route('/')
def index() -> str:
    return """
<form method="POST" action="/upload" enctype="multipart/form-data">
    <input type="datos" name="datos">
    <input type="submit">
</form>
"""
@app.route('/upload', methods=['POST'])
def upload(csvdata, bucketname, blobname):
    client = storage.Client()
    bucket = client.get_bucket(bucketname)
    blob = bucket.blob(blobname)
    blob.upload_from_string(csvdata)
    gcslocation = 'gs://{}/{}'.format(bucketname, blobname)
    logging.info('Uploaded {} ...'.format(gcslocation))
    return gcslocation

@app.errorhandler(500)
def server_error(e: Union[Exception, int]) -> str:
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500
#-----------------------------------------------------

CERTS = None
AUDIENCE = None

def certs():
    """Returns a dictionary of current Google public key certificates for
    validating Google-signed JWTs. Since these change rarely, the result
    is cached on first request for faster subsequent responses.
    """
    import requests

    global CERTS
    if CERTS is None:
        response = requests.get(
            'https://www.gstatic.com/iap/verify/public_key'
        )
        CERTS = response.json()
    return CERTS

def get_metadata(item_name):
    """Returns a string with the project metadata value for the item_name.
    See https://cloud.google.com/compute/docs/storing-retrieving-metadata for
    possible item_name values.
    """
    import requests

    endpoint = 'http://metadata.google.internal'
    path = '/computeMetadata/v1/project/'
    path += item_name
    response = requests.get(
        '{}{}'.format(endpoint, path),
        headers={'Metadata-Flavor': 'Google'}
    )
    metadata = response.text
    return metadata

def audience():
    """Returns the audience value (the JWT 'aud' property) for the current
    running instance. Since this involves a metadata lookup, the result is
    cached when first requested for faster future responses.
    """
    global AUDIENCE
    if AUDIENCE is None:
        project_number = get_metadata('numeric-project-id')
        project_id = get_metadata('project-id')
        AUDIENCE = '/projects/{}/apps/{}'.format(
            project_number, project_id
        )
    return AUDIENCE

def validate_assertion(assertion):
    """Checks that the JWT assertion is valid (properly signed, for the
    correct audience) and if so, returns strings for the requesting user's
    email and a persistent user ID. If not valid, returns None for each field.
    """
    from jose import jwt
    try:
        info = jwt.decode(
            assertion,
            certs(),
            algorithms=['ES256'],
            audience=audience()
            )
        return info['email'], info['sub']
    except Exception as e:
        print('Failed to validate assertion: {}'.format(e), file=sys.stderr)
        return None, None

@app.route('/', methods=['GET'])
def say_hello():
    from flask import request
    assertion = request.headers.get('X-Goog-IAP-JWT-Assertion')
    email, id = validate_assertion(assertion)
    page = "<h1>Hello {}</h1>".format(email)
    return page

#------------------------------------------------------

# Path del modelo preentrenado
MODEL_PATH = 'models/pickle_model.pkl'

# Se recibe la imagen y el modelo, devuelve la predicción
def model_prediction(x_in, model):

    x = np.asarray(x_in).reshape(1,-1)
    preds=model.predict(x)

    return preds

def main():
    
    model=''

    # Se carga el modelo
    if model=='':
        with open(MODEL_PATH, 'rb') as file:
            model = pickle.load(file)
    
    # Configura titulo e icon de pagina        
    st.set_page_config(page_title="Modelo Analítico ELX", page_icon="img/Icono.ico", layout="wide")

    # Menú y logo
    st.sidebar.image("img/logo3.png")
    st.sidebar.write("")

    #Estilo botón
    st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color:#461e7d;
                color:#ffffff
            }
            div.stButton > button:hover {
                background-color:#f0f2f6;
                color:#461e7d
            }
            </style>""", unsafe_allow_html=True)

    a, b, c = False, False, False
                
    with st.sidebar.expander("MODELO MÚLTIPLES CLIENTES ", expanded = False):
        # uploading files
        datos = st.file_uploader("Subir archivos: ", type = ["xlsx"])
 
        if datos is not None:
            # To read file as bytes:
            ##bytes_data = datos.getvalue()
            
            # To convert to a string based IO:
            ##stringio = StringIO(datos.getvalue().decode("utf-8"))

            # To read file as string:
            ##string_data = stringio.read()

            # Can be used wherever a "file-like" object is accepted:
            dataframe = pd.read_excel(datos,index_col=False)
            
            #subir archivo al bucket en gcloud
            #urlarchivo = upload(bytes_data,CLOUD_STORAGE_BUCKET,'datos')
        
        b = st.button("Ejecutar Modelo",type="primary")


    with st.sidebar.expander("MODELO UNITARIO ", expanded = False):
        # Lectura de datos
        nit = st.number_input("Digite el número del Nit:",value=1,max_value=999999999)
        actEcon = st.selectbox("Actividad económica:",['Industrial','Servicios','Transporte',
                               'Comercio','Construcción','Energético','Financiero','Comunicaciones','Agropecuario'])
        tamEmp = st.selectbox("Tamaño de la empresa:",['Gran Empresa','Mediana Empresa','Pequeña Empresa'])
        flegal = st.selectbox("Forma Legal:",['S.A.S.','LTDA.','S.A.','ESAL','Persona Jurídica','Sucursal Extranjera',
                                              'S.C.A.','Undefined','Persona Natural','S.C.S.'])
        numEmpl = st.number_input("Número de empleados:",value=1)
        activos = st.number_input("Activos Totales:")
        ingresosOp = st.number_input("Total Ingresos Operativos:")
        TotPatr = st.number_input("Total Patrimonio:")
        ganDespImpto = st.number_input("Ganancias después de Impuestos:")
        edadEmp = st.number_input("Edad de la Empresa:",value=1)
                
        # button
        c = st.button("Ejecutar Modelo 1",type="primary")
        
    with st.sidebar.expander("CUSTOMER JOURNEY ", expanded = False):
        a = st.button("Visualizar",type="primary")        


    if a == False and b == False and c == False:
        st.image("img/Img_presentacion2.jpg",use_column_width="always")
    elif a == True:
        with st.container():
            st.write("""
            # Simple Stock Price App
            Shown are the stock **closing price** and ***volume*** of Google!
            """)

            # https://towardsdatascience.com/how-to-get-stock-data-using-python-c0de1df17e75
            #define the ticker symbol
            tickerSymbol = 'GOOGL'
            #get data on this ticker
            tickerData = yf.Ticker(tickerSymbol)
            #get the historical prices for this ticker
            tickerDf = tickerData.history(period='1d', start='2010-5-31', end='2020-5-31')
            # Open	High	Low	Close	Volume	Dividends	Stock Splits

            col1, col2 = st.columns(2)
            col1.write("""
            ## Closing Price
            """)
            col1.line_chart(tickerDf.Close)
            col2.write("""
            ## Volume Price
            """)
            col2.line_chart(tickerDf.Volume)

    elif b == True:
        st.markdown("<h1 style='text-align: center;'>Modelo Analítico ELX</h1>", unsafe_allow_html=True)
        st.write("")
        vista1,vista2 = st.tabs(["RESULTADO MODELO ELX", "REPORTE DESCRIPTIVO"])
        
        with vista1:
            #dataframe = pd.read_csv(datos)
            
            #dataframe = pd.read_csv('./Crop_recommendation.csv','r')
            st.write("")
            st.write(dataframe)
            
            def convert_df(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv().encode('utf-8')

            csv = convert_df(dataframe)
            
            st.download_button(
                label="Descargar archivo",
                data=csv,
                file_name='Resultado_df.csv',
                mime='text/csv',
            )
            
        with vista2:
            tab1, tab2, tab3,tab4 = st.tabs(["Consumo", "Ventas", "Económico","Demográficas"])
            source = dataframe
            with tab1:
                st.write("")
                st.write("")
                st.subheader("CONSUMO")
                col7,col8 = st.columns(2) 
                #col8.image("img/cons.png",use_column_width="always")
                bar= alt.Chart(source).mark_bar().encode(x='count()',y="RangoConsumo:N").configure_mark(color='#566573')
                col7.altair_chart(bar,use_container_width=True,theme="streamlit")
                st.write("")
            with tab2:
                st.write("")
                st.write("")
                st.subheader("VENTAS")
                col1,col2 = st.columns(2, gap="medium")     
                #col1.image("img/ven1.png")
                bar= alt.Chart(source).mark_bar().encode(x='count()',y="RangodeCompra($):N").configure_mark(color='#566573')
                col1.altair_chart(bar,use_container_width=True,theme="streamlit")
                #col2.image("img/ven2.png")
                bar= alt.Chart(source).mark_bar().encode(x='count()',y="RangoRecurrenciaCompra:N").configure_mark(color='#566573')
                col2.altair_chart(bar,use_container_width=True,theme="streamlit")
                #col1.image("img/ven5.png")
                bar= alt.Chart(source).mark_bar().encode(x='count()',y="TipoCliente#Oportunidades:N").configure_mark(color='#566573')
                col1.altair_chart(bar,use_container_width=True,theme="streamlit")
                #col2.image("img/ven6.png")
                bar= alt.Chart(source).mark_bar().encode(x='count()',y="TipoCliente$Oportunidades:N").configure_mark(color='#566573')
                col2.altair_chart(bar,use_container_width=True,theme="streamlit")
                #col1.image("img/ven3.png")
                bar= alt.Chart(source).mark_bar().encode(x='count()',y="ClusterComprados:N").configure_mark(color='#566573')
                col1.altair_chart(bar,use_container_width=True,theme="streamlit")
                st.write("")
            with tab3:
                st.write("")
                st.write("")
                st.subheader("ECONOMICAS")
                col4,col5 = st.columns(2,gap="medium")  
                #col5.image("img/econ3.png")
                bar= alt.Chart(source).mark_bar().encode(x='count()',y="TamanoEmpresa:N").configure_mark(color='#566573')
                col4.altair_chart(bar,use_container_width=True,theme="streamlit")   
                #col4.image("img/econ1.png")
                bar= alt.Chart(source).mark_bar().encode(x='count()',y="CategorizacionSectores:N").configure_mark(color='#566573')
                col5.altair_chart(bar,use_container_width=True,theme="streamlit")
                #col4.image("img/econ2.png")
                bar= alt.Chart(source).mark_bar().encode(x='count()',y="EstatusOperacional:N").configure_mark(color='#566573')
                col4.altair_chart(bar,use_container_width=True,theme="streamlit")
                st.write("")
            with tab4:
                st.write("")
                st.write("")
                st.subheader("DEMOGRÁFICAS")
                col9,col0 = st.columns(2)
                #col9.image("img/dem.png",use_column_width="always")
                bar= alt.Chart(source).mark_bar().encode(x='count()',y="CategoriaDepartamento:N").configure_mark(color='#566573')
                col9.altair_chart(bar,use_container_width=True,theme="streamlit")
                st.write("")
                

    elif c == True:
        st.image("img/Modelo1.png",use_column_width="always")
        #st.write("")
        #x_in =[np.float_(N.title()),
        #            np.float_(P.title()),
        #            np.float_(K.title()),
        #            np.float_(Temp.title()),
        #            np.float_(Hum.title()),
        #            np.float_(pH.title()),
        #            np.float_(rain.title())]
        #predictS = model_prediction(x_in, model)
        #st.success('EL CULTIVO RECOMENDADO ES: {}'.format(predictS[0]).upper())
        #st.write("")
        #if datos != '':
        #    dataframe = pd.read_csv(datos)
        #    st.write(dataframe.head())
            
        #    def convert_df(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
        #        return df.to_csv().encode('utf-8')

        #    csv = convert_df(dataframe)
            
        #    st.download_button(
        #        label="Descargar archivo",
        #        data=csv,
        #        file_name='large_df.csv',
        #        mime='text/csv',
        #    )
        #st.download_button("Descargar archivo",data=datos)

if __name__ == '__main__':
    main()
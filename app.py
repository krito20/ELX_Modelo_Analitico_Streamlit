import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template, url_for
import pickle
from sklearn import svm
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl

#-------------------------------------------------------IAP GCP
app = Flask(__name__)

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
    st.set_page_config(page_title="Modelo Analítica ELX", page_icon="img/Icono.ico", layout="wide")

    # Menú y logo
    st.sidebar.image("img/logo3.png")
    st.sidebar.write("")


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
    datos =''
    # Title
    #st.title("Customer Analytics")
                

    with st.sidebar.expander("CUSTOMER JOURNEY: ", expanded = False):
        #if st.sidebar.button("Mi primer opción Modelo"):
        a = st.button("Visualizar",type="primary")


    with st.sidebar.expander("MODELO MÚLTIPLES CLIENTES: ", expanded = False):
        #if st.sidebar.button("Mi primer opción Modelo"):
        # uploading files
        datos = st.file_uploader("Subir archivos: ", type = ["csv"])
        print(type(datos))
        #st.image(data)
        b = st.button("Ejecutar Modelo",type="primary")


    with st.sidebar.expander("MODELO RECOMENDACIÓN UNITARIA: ", expanded = False):
        #if st.sidebar.button("Mi primer opción Modelo"):
        # select boxes
        #selec_item = st.selectbox("Variable 1", ["A","B","C","D"])
        #selec_item = st.selectbox("Variable 2", ["1","3","6","9"])
        #selec_item = st.selectbox("Variable 3", ["Ltda","S.A.S"])
        # slider
        #range_var = st.slider("Variable 5:", 1,5)
        #range_var = st.slider("Variable 6:", 1000000,5000000)
        
        # Lecctura de datos

        N = st.text_input("Nitrógeno:",placeholder=94)
        P = st.text_input("Fósforo:",placeholder=53)
        K = st.text_input("Potasio:",placeholder=40)
        Temp = st.text_input("Temperatura:",placeholder=20.2)
        Hum = st.text_input("Humedad:",placeholder=82.9)
        pH = st.text_input("pH:",placeholder=5.7)
        rain = st.text_input("Lluvia:",placeholder=241.9)
                
        # button
        c = st.button("Ejecutar Modelo2",type="primary")


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
            
            #-----------------------------------------------------------------
            
            class Visuals():
  
                def __init__(self,df):
                    self.df = df

                def ValidarCampos(self):
                    lista_campos = ['RangoConsumo','RangodeCompra($)','RangoRecurrenciaCompra','ClusterComprados',
                                'TipoCliente#Oportunidades','TipoCliente$Oportunidades','CategorizacionSectores',
                                'ESTATUSOPERACIONAL','TamanoEmpresa','CategoriaDepartamento']
                    for campo in lista_campos:
                        if campo in df.columns.to_list():
                            pass
                        else: 
                                print('El campo ', '"'+campo+'"', ' no se encuentra en el archivo cargado, por favor valide que el archivo contenga el campo ', '"'+campo+'"')
                
                # def Validar_categorias_por_campo(self):
                #   cat_rango

                def Graficar(self, variable ):
                    # variable 
                    mpl.rcParams['font.size'] = 12
                    mpl.rcParams['font.family'] = 'sans-serif'
                    color = '#461e7d'
                    df_f = df.copy()
                    df_f[variable].fillna('Sin Catalogar', inplace=True)                 

                    orden = ['Sin Catalogar', 'Menor a 5000', 'Entre 5000 y 10000', 'Entre 10000 y 55000', 'Mayor a 55000']

                    values = df_f[variable].value_counts().keys().to_list()
                    n_barras = len(values)
                    
                    #total = df_f.count(axis=1)
                    #fig = plt.barh(total.index, total)
                    #st.pyplot(fig)

                    plt.figure(figsize = (7,5))

                    ax = sns.countplot(y=variable, order = orden, data=df_f, color = color #[(70/255,30/255,125/255)]
                                    , orient = 'h')#, hue = 'Tipo de usuario', hue_order=df["Tipo de usuario"].value_counts().keys().tolist())

                    for i in range(n_barras):
                        p = ax.patches[i]
                        total = len(df_f) 
                    
                    ax.annotate(format(p.get_width(), '.0f') + ' ('+format(p.get_width()/total*100, '.2f')+' %)', 
                                (p.get_width(), p.get_y() + p.get_height()), # (p.get_x() + p.get_width() / 2., p.get_height())
                                ha='center', va='center',
                                xytext=(50, 20),
                                textcoords='offset points')


                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['bottom'].set_visible(False)
                    ax.spines['left'].set_visible(False)

                    plt.xticks([])
                    # plt.axis('off')
                    plt.title('')
                    plt.xlabel('Cantidad de Registros')
                    
                    if variable == 'RangoConsumo':
                        plt.ylabel('Rango de Consumo')

                        #plt.show()
                    
            sheet_name = 'Data'
            path = './Ejemplo_prueba_cartera.xlsx'
            df = pd.read_excel(path, sheet_name= sheet_name)

            ob = Visuals(df)
            ob.ValidarCampos()
            ob.Graficar('RangoConsumo')

    elif b == True:
        st.title("Modelo Múltiples Registros")
        tab1, tab2, tab3,tab4 = st.tabs(["CONSUMO", "VENTAS", "ECONOMICAS","DEMOGRÁFICAS"])
        with tab1:
            st.write("")
            st.subheader("CONSUMO")
            col7,col8 = st.columns(2) 
            st.image("img/cons.png",use_column_width="always")
            st.write("")
        with tab2:
            st.write("")
            st.subheader("VENTAS")
            col1,col2 = st.columns(2)     
            col1.image("img/ven1.png")
            col2.image("img/ven2.png")
            col1.image("img/ven5.png")
            col2.image("img/ven6.png")
            col1.image("img/ven3.png")
            #col3.image("img/Ventas6.png")
            st.write("")
        with tab3:
            st.write("")
            st.subheader("ECONOMICAS")
            col4,col5 = st.columns(2)     
            col4.image("img/econo1.png")
            col5.image("img/econo3.png")
            col4.image("img/econo2.png")
            st.write("")
        with tab4:
            st.write("")
            st.subheader("DEMOGRÁFICAS")
            col9,col0 = st.columns(2)
            st.image("img/dem.png",use_column_width="always")
            st.write("")
            
        #st.image("img/Modelo2.png",use_column_width="always")
        #st.write("")
        
        dataframe = pd.read_csv(datos)
        #st.write(dataframe.head())
        
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode('utf-8')

        csv = convert_df(dataframe)

        st.download_button(
            label="Descargar archivo",
            data=csv,
            file_name='large_df.csv',
            mime='text/csv',
        )
        #st.download_button("Descargar archivo",data=datos)
        
    elif c == True:
        #st.image("img/Modelo1.png",use_column_width="always")
        #st.write("")
        x_in =[np.float_(N.title()),
                    np.float_(P.title()),
                    np.float_(K.title()),
                    np.float_(Temp.title()),
                    np.float_(Hum.title()),
                    np.float_(pH.title()),
                    np.float_(rain.title())]
        predictS = model_prediction(x_in, model)
        st.success('EL CULTIVO RECOMENDADO ES: {}'.format(predictS[0]).upper())
        st.write("")
        if datos != '':
            dataframe = pd.read_csv(datos)
            st.write(dataframe.head())
            
            def convert_df(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv().encode('utf-8')

            csv = convert_df(dataframe)
            
            st.download_button(
                label="Descargar archivo",
                data=csv,
                file_name='large_df.csv',
                mime='text/csv',
            )
        #st.download_button("Descargar archivo",data=datos)

if __name__ == '__main__':
    main()
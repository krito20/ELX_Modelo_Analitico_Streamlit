import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template, url_for
import pickle
from sklearn import svm

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

    # logo
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
        
        

    with st.sidebar.expander("REPORTE ANALÍTICA: ", expanded = False):
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
    elif b == True:
        st.image("img/Modelo2.png",use_column_width="always")
        st.write("")
        
        dataframe = pd.read_csv(datos)
        st.write(dataframe.head())
        
        @st.cache
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
            
            @st.cache
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
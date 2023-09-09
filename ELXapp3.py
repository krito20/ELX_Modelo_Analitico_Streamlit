import streamlit as st

import yfinance as yf


st.set_page_config(page_title="Modelo Analítica ELX", page_icon="img/Icono.ico", layout="wide")

# logo
#st.sidebar.image("img/logo1.jpg")
st.sidebar.image("img/logo3.png")

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

#selec_item = st.sidebar.selectbox("Select option", ["Customer Journey","Modelo Unitario","Modelo Múltiple"])
#estado = st.sidebar.radio("Seleccione la opción que desea visualizar: ", ("Customer Journey", "Modelo Unitario", "Modelo Múltiple"))
a, b, c, d, e = False, False, False, False, False
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
a = st.sidebar.button("Ver el Customer Journey",type="primary")
#st.sidebar.write(a)
d = st.sidebar.button("Modelo  Cliente Múltiple",type="primary")
#st.sidebar.write(d)
e = st.sidebar.button("Modelo  Cliente Unitario",type="primary")
#st.sidebar.write(e)
#st.sidebar.write(b)
#st.sidebar.write(c)

if a == False and d == False and e == False and b == False and e == False:
    st.image("img/Img_presentacion2.jpg",use_column_width="always")
else:
    if d == True:
        #with st.container():
        # uploading files
        data = st.file_uploader("Subir archivos: ", type = ["csv"])
        #st.image(data)
        b=st.button("Ejecutar Modelo")
                        
                        
    elif e == True:
        with st.container():
            col4, col5 = st.columns(2)
            # select boxes
            selec_item = col4.selectbox("Variable 1", ["A","B","C","D"])
            selec_item = col5.selectbox("Variable 2", ["1","3","6","9"])
            selec_item = col4.text_input("Variable 3")
            selec_item = col5.text_input("Variable 4")
            # slider
            range_var = col4.slider("Variable 5:", 1,5)
            range_var = col5.slider("Variable 6:", 1000000,5000000)
            # button
        c= col4.button("Ejecutar Modelo2")

    else:
        if a == True:
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
        elif c == True:
            st.image("img/Modelo1.png",use_column_width="always")


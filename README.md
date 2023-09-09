# API_Gcloud_Streamlit
Generaremos una aplicación que permite ejecutar un modelo de ML para generar las estimaciones a partir de una serie de criterios, el resultado del modelo de recomendación se puede ejecutar para 1 cliente o para muchos contenidos en un archivo. También se proyecta incluir un módulo para presentar un informe resumen del Customer Journey del cliente, como Análisis de las variables relacionadas en el proceso y lo pondremos en producción usando Streamlit y Google Cloud. El modelo permitirá recomendar la mayor probabilidad de compra de un producto en Enel X.

##  1. Entrenamiento del modelo


##  2. Producción en servidor local - preparación del entorno

Creamos un entorno con python 3.11.1, e instalamos las dependencias necesarias.

    $   conda create -n myenvapp1
    $   conda activate myenvapp1
    $   conda install python=3.11.1
    $   pip install -r requirements.txt
    $   streamlit run app.py
    
##  3. Producción en servidor remoto

    *   Activar una cuenta en google cloud
    *   Crear proyecto en google cloud
    *   Instalar GoogleCloudSDK
        (https://cloud.google.com/sdk/docs/install)
    *   Ejecutar en la terminal:
    
    $ gcloud init
    $ gcloud app deploy app.yaml --project "nombre proyecto en GCloud"

    $ gcloud components update



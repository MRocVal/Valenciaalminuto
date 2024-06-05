#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 18:31:11 2024

@author: manuelrocamoravalenti
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import yagmail

# ::::::::::::::::::::::::::::: FUNCIONES ::::::::::::::::::::::::::::::::

# Función para obtener próximas llegadas o salidas
def obtener_proximos_movimientos(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer la información específica de llegadas o salidas
        movimientos = []
        for div in soup.find_all('div', style=lambda value: value and 'padding-left: 5px' in value):
            # Extraer el número de la línea desde la URL de la imagen
            numero_linea = div.find('img')['src'].split('_')[-1].split('.')[0]
            destino = div.find('b').text.strip()  # Extrae el destino
            tiempo = div.find_all('span')[-1].text.strip()  # Extrae el tiempo
            movimientos.append({
                "Número de Línea": numero_linea,
                "Destino": destino,
                "Tiempo": tiempo
            })
        
        return movimientos
    except requests.RequestException as e:
        st.error(f"Error al obtener los datos de {url}: {e}")
        return []
    
def obtener_proximos_movimientos_bus(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica si la solicitud fue exitosa
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer la información específica de llegadas o salidas
        movimientos = []
        for div in soup.find_all('div', style=lambda value: value and 'padding-left: 5px' in value):
            imagen = div.find('img')
            if imagen:
                # Extraer el número de la línea desde la URL de la imagen
                numero_linea = imagen['src'].split('_')[-1].split('.')[0]
            else:
                numero_linea = "Desconocido"

            b_tag = div.find('b')
            if b_tag:
                destino = b_tag.text.strip()  # Extrae el destino
            else:
                destino = "Destino desconocido"

            span_tags = div.find_all('span')
            if span_tags:
                # Extrae el tiempo y lo deja en el formato deseado (P. Congressos - 21 min)
                tiempo = span_tags[-1].text.strip()  
            else:
                tiempo = "Tiempo desconocido"

            movimientos.append({
                "Número de Línea": numero_linea,
                "Destino": destino,
                "Tiempo": tiempo
            })
        
        return movimientos
    except requests.RequestException as e:
        st.error(f"Error al obtener los datos de {url}: {e}")
        return []


def calcular_tiempo_restante(hora_llegada):
    formato = '%H:%M:%S'
    try:
        ahora = datetime.now().strftime(formato)
        hora_actual = datetime.strptime(ahora, formato)
        hora_llegada_dt = datetime.strptime(hora_llegada, formato)

        # Si la hora de llegada es menor a la hora actual, añadir un día
        if hora_llegada_dt < hora_actual:
            hora_llegada_dt += timedelta(days=1)

        tiempo_restante = hora_llegada_dt - hora_actual
        tiempo_restante_str = str(tiempo_restante)
        
        if tiempo_restante_str == '<Na>':
            return '+1 hora'
    

        # Buscar y extraer solo los minutos y segundos
        minutos_segundos = tiempo_restante_str.split(":")[1:]
        return ":".join(minutos_segundos)
    except ValueError:
        return '+1 hora'



def calcular_tiempo_restante_bus(hora_llegada):
    try:
        # Extraer solo los minutos del texto
        minutos = int(hora_llegada.split('min')[0].split('-')[-1].strip())
        tiempo_restante = timedelta(minutes=minutos)
        # Formatear el tiempo restante para mostrar solo horas y minutos
        tiempo_restante_str = f'{tiempo_restante.seconds//3600:02d}:{(tiempo_restante.seconds//60)%60:02d}'
        return tiempo_restante_str
    except ValueError:
        return "Tiempo desconocido"

# :::::::::::::::::::::::::::: INTERFAZ DE USUARIO :::::::::::::::::::::::::::::


# Cargar los datos
data = pd.read_csv('fgv-bocas.csv', delimiter=';')
data_EMT = pd.read_csv('emt.csv', delimiter=';')

# Menú de navegación en la barra lateral
pagina = st.sidebar.selectbox('Selecciona una página', ['Home','MetroValencia Schedule','EMT Schedules', 
                                                        'EMT Map','ValenBici'])

if pagina == 'Home':
    
    st.image('1.jpg')
    st.title("VALENCIA IN A MINUTE")
    
    # Sección para próximas llegadas y salidas
    st.markdown("""
Our application emerges from the need to provide a tool that updates in real time and offers precise and reliable information on the arrival of subways. In a world where time is invaluable, we understand the importance of minimizing waiting times and optimizing the journeys of passengers.

## Real-Time Updates

The main feature of our application is its ability to update in real time. This means that users can get instant information about subway arrivals, with measured and accurate times that allow them to plan their commutes efficiently. You will never have to guess when the next subway will arrive; our app will tell you instantly.

## Improved Organization for Passenger Journeys

In addition to providing exact schedules, our application is designed to enhance the organization of passengers' journeys. With advanced features, users can plan their routes, receive notifications about changes and delays, and access recommendations for the fastest and most convenient routes. Our goal is to make each journey as smooth and stress-free as possible.

## A Solution to Your Transportation Needs

In summary, our application arises from the need for a solution that offers real-time updates and superior organization for subway journeys. We are committed to innovation and continuous improvement so that your travel experience is optimal, efficient, and enjoyable. Join us and discover a new way to travel by subway.

Additionally, we also have schedules for EMT buses and a page for calculating route duration between Valenbisi station stops.

## Contact

For any suggestions or inquiries, please send an email to the following address: [mrocval@etsinf.upv.es](mailto:mrocval@etsinf.upv.es).

""")
    
elif pagina == 'MetroValencia Schedule':
    data = pd.read_csv('fgv-bocas.csv', delimiter=';')
    # Sección para próximas llegadas y salidas
    st.markdown("""
                
    # Next Arrivals and Departures
    A new way to quickly check the next arrivals and departures at your stop.
    Select a metro station and get updated information on the next trains arriving or departing from there.
    
    """)
    
    st.image('foto_metro.jpeg')

    # Filtrar datos para la selección de estaciones y ordenar alfabéticamente
    estaciones = sorted(data['Denominació / Denominación'].unique())
    
    st.markdown("""
                
    You can try entering ‘benimac’ and pressing enter.
    """)

    # Entrada de texto para la estación
    estacion_input = st.text_input('Enter the Station Name: ')
    estaciones_filtradas = [estacion for estacion in estaciones if estacion_input.lower() in estacion.lower()]

    estacion_seleccionada = st.selectbox('Select a Station:', estaciones_filtradas)

    if estacion_seleccionada:
        # Verificar si la estación ingresada existe en el DataFrame
        if estacion_seleccionada in data['Denominació / Denominación'].values:
            url_llegadas = data[data['Denominació / Denominación'] == estacion_seleccionada]['Pròximes Arribades / Próximas llegadas'].values[0]

            llegadas = obtener_proximos_movimientos(url_llegadas)

            # Calcular el tiempo restante para llegadas
            for llegada in llegadas:
                llegada["Tiempo Restante"] = calcular_tiempo_restante(llegada["Tiempo"])

            st.markdown(f"#### Next Arrivals for the Station: {estacion_seleccionada}")
            df_llegadas = pd.DataFrame(llegadas).sort_values(by="Destino")
            st.table(df_llegadas)

            # Añadir una pausa de 60 segundos para la actualización
            time.sleep(1)
            st.experimental_rerun()

        else:
            st.write("The station entered is not found in the dataset.")

elif pagina == 'Interactive Map':
    # Descripción de la aplicación
    
    st.markdown("""
    # Interactive Map of Metro Lines
    This map shows the locations of selected metro stations.
    You can choose the metro lines you are interested in and see their geographical distribution.
    
    """)

    # Agregar una foto
    st.image('Plano_general.jpg')

    st.markdown("""
        **Select** the lines you need to consult; the different available stations will appear on the map.
    """)

    # Asegurar que los tipos de datos sean correctos
    data[['latitude', 'longitude']] = data['geo_point_2d'].str.split(',', expand=True).astype(float)

    # Obtener líneas únicas del conjunto de datos
    lines = data['Línies / Líneas'].unique()  # Ajustar el nombre de la columna según tu conjunto de datos

    # Checkbox para seleccionar todas las líneas
    if st.checkbox('Select All Lines'):
        selected_lines = lines
    else:
        selected_lines = st.multiselect('Select Metro Lines:', options=lines)

    # Filtrar datos en función de las líneas seleccionadas
    filtered_data_lines = data[data['Línies / Líneas'].isin(selected_lines)]

    # Verificar si hay datos para mostrar
    if not filtered_data_lines.empty:
        # Agregar datos de ícono a los datos filtrados
        filtered_data_lines['icon_data'] = filtered_data_lines.apply(lambda row: {
            'url': 'https://cdn-icons-png.flaticon.com/128/684/684908.png',
            'width': 128,
            'height': 128,
            'anchorY': 128,
        }, axis=1)

        # Definir el estado inicial del mapa
        view_state = pdk.ViewState(
            latitude=filtered_data_lines['latitude'].mean(),
            longitude=filtered_data_lines['longitude'].mean(),
            zoom=11,
            pitch=50
        )

        # Definir la capa de íconos
        icon_layer = pdk.Layer(
            type='IconLayer',
            data=filtered_data_lines,
            get_icon='icon_data',
            get_size=2.5,
            size_scale=15,
            get_position='[longitude, latitude]',
            pickable=True,
        )

        # Crear el mapa con vista satelital
        map = pdk.Deck(
            layers=[icon_layer],
            initial_view_state=view_state,
            map_style='mapbox://styles/mapbox/satellite-v9'  # Usando la vista satelital de Mapbox
        )

        st.pydeck_chart(map)
    else:
        st.write("No data available for the selected lines.")

elif pagina == 'Arrival notification by email':

    
    # Mostrar imagen
    st.image('estacion_T.jpg')
    
    # Texto introductorio
    st.markdown("""
    # Next Arrivals and Departures by Email
    ### Tired of missing the subway?
    
    We've got the perfect solution for you! Just enter your email, pick your stop, and choose how many minutes in advance you need updates. You'll get an email with the latest info on your stop every minute.
    
    Say goodbye to being late for your appointments or work!
    """)
    
    # Carga los datos de las estaciones de metro
    def load_metro_data():
        return pd.read_csv('fgv-bocas.csv', delimiter=';')
    
    # Función para obtener las próximas llegadas de la estación
    def obtener_proximos_movimientos(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        movimientos = []
        for div in soup.find_all('div', style=lambda value: value and 'padding-left: 5px' in value):
            numero_linea = div.find('img')['src'].split('_')[-1].split('.')[0]
            destino = div.find('b').text.strip()
            tiempo = div.find_all('span')[-1].text.strip()
            movimientos.append({"Número de Línea": numero_linea, "Destino": destino, "Tiempo": tiempo})
        return movimientos
    
    # Función para calcular el tiempo restante
    def calcular_tiempo_restante(hora_llegada):
        formato = '%H:%M:%S'
        ahora = datetime.now().strftime(formato)
        hora_actual = datetime.strptime(ahora, formato)
        hora_llegada_dt = datetime.strptime(hora_llegada, formato)
        if hora_llegada_dt < hora_actual:
            hora_llegada_dt += timedelta(days=1)
        tiempo_restante = hora_llegada_dt - hora_actual
        return int(tiempo_restante.total_seconds() / 60)  # Devuelve el tiempo en minutos
    
    # Función para enviar correos electrónicos con yagmail
    def send_email(to_email, subject, message):
        yag = yagmail.SMTP('mrocval018@gmail.com', 'qppo ppbx zpny ygbo')
        try:
            yag.send(to=to_email, subject=subject, contents=message)
            st.success('Email sent successfully!')
        except Exception as e:
            st.error(f'An error occurred: {e}')
    
    # Cargar los datos de las estaciones
    metro_data = load_metro_data()
    
    # Selección de estación
    estaciones = sorted(metro_data['Denominació / Denominación'].unique())
    estacion_seleccionada = st.selectbox('Select a Station:', estaciones)
    
    # Entrada para correo electrónico del usuario
    user_email = st.text_input('Enter your email for notifications')
    
    # Tiempo de alerta antes de la llegada
    alert_time = st.number_input('Alert me X minutes before arrival:', min_value=1, max_value=60, value=10)
    
    # Diccionario para rastrear si ya se ha enviado un correo para una llegada específica
    if 'emails_sent' not in st.session_state:
        st.session_state['emails_sent'] = {}
    
    # Bandera para seguir verificando las llegadas
    if 'checking_arrivals' not in st.session_state:
        st.session_state['checking_arrivals'] = False
    
    def check_arrivals():
        if estacion_seleccionada and user_email:
            url_llegadas = metro_data[metro_data['Denominació / Denominación'] == estacion_seleccionada]['Pròximes Arribades / Próximas llegadas'].values[0]
            llegadas = obtener_proximos_movimientos(url_llegadas)
            alert_llegadas = []
            for llegada in llegadas:
                tiempo_restante = calcular_tiempo_restante(llegada["Tiempo"])
                if tiempo_restante <= alert_time:
                    alert_llegadas.append(f"Línea {llegada['Número de Línea']} hacia {llegada['Destino']} en {tiempo_restante} minutos")
            if alert_llegadas:
                subject = 'Your Metro Arrivals'
                message = "The following metros are arriving soon:\n" + "\n".join(alert_llegadas)
                send_email(user_email, subject, message)
                st.success(f'Email sent with the following arrivals:\n{message}')
            df_llegadas = pd.DataFrame(llegadas)
            st.table(df_llegadas)
    
    if st.button('Check for Arrivals') or st.session_state['checking_arrivals']:
        st.session_state['checking_arrivals'] = True
        check_arrivals()
        time.sleep(60)
        st.experimental_rerun()
    
    # Instrucciones adicionales
    st.markdown("""
    #### Additional Information
    This application is designed to provide real-time updates and organize travel efficiently. You can plan your routes, receive notifications about changes and delays, and access recommendations for the quickest and most convenient trips. Join us and discover a new way to travel by metro.
    """)

elif pagina == 'EMT Schedules':
    st.markdown("""
    # Next Bus Arrivals
    Quickly check the next arrivals at your bus stop.
    Select a stop and get updated information on the upcoming buses.
    """)
    st.image('bus.jpg')  # Ensure you have an appropriate image or remove this line

    # Filter data for bus stop selection and sort alphabetically
    paradas = sorted(data_EMT['Denominació / Denominación'].unique())

    # Text input for the bus stop
    parada_input = st.text_input('Enter the name or number of the stop:')
    paradas_filtradas = [parada for parada in paradas if parada_input.lower() in parada.lower()]

    parada_seleccionada = st.selectbox('Select a stop:', paradas_filtradas)

    if parada_seleccionada:
        try:
            # Verify if the entered stop exists in the DataFrame
            if parada_seleccionada in data_EMT['Denominació / Denominación'].values:
                url_llegadas = data_EMT[data_EMT['Denominació / Denominación'] == parada_seleccionada]['Pròximes Arribades / Proximas Llegadas'].values[0]

                llegadas = obtener_proximos_movimientos_bus(url_llegadas)

                # Calculate the remaining time for arrivals
                for llegada in llegadas:
                    llegada["Tiempo Restante"] = calcular_tiempo_restante_bus(llegada["Tiempo"])

                st.markdown(f"### Next arrivals for the stop: {parada_seleccionada}")
                df_llegadas = pd.DataFrame(llegadas).sort_values(by="Tiempo Restante")

                df_llegadas['Tiempo'].apply(lambda x: st.markdown(f"<h3 style='font-size:50px;'>{x}</h3>", unsafe_allow_html=True))

                # Add a 60-second pause for the update
                time.sleep(60)
                st.experimental_rerun()
            else:
                st.write("The stop entered is not found in the dataset.")
        except KeyError:
            st.write("No buses available at this moment.")
        except Exception as e:
            st.write("An error occurred. Please try again later.")
    
elif pagina == 'EMT Map':
    import pandas as pd
    import pydeck as pdk
    import streamlit as st

    # Descripción de la aplicación
    st.markdown("""
                
    # Interactive Map of EMT Bus Stops
Welcome to the interactive visualization of EMT bus stops in Valencia.
This map shows the locations of selected bus stops.
You can choose the stops you are interested in and see their geographical distribution.
    
    """)

    # Agregar una foto
    st.image('esat.jpg')

    # Cargar y preparar los datos
    def load_data():
        data = pd.read_csv('emt.csv', delimiter=';')
        data['lon'], data['lat'] = zip(*data['geo_point_2d'].apply(lambda x: (float(x.split(',')[1]), float(x.split(',')[0]))))
        return data

    data = load_data()

    # Entrada para filtrar paradas por nombre
    filter_query = st.text_input('Filter stops by name: ')

    # Filtrar las paradas que coincidan con la entrada del usuario
    if filter_query:
        filtered_stops = data[data['Denominació / Denominación'].str.contains(filter_query, case=False, na=False)]
    else:
        filtered_stops = data

    selected_stop = None

    # Checkbox para seleccionar todas las paradas
    if st.checkbox('Select All Stops'):
        selected_stops = filtered_stops
    else:
        selected_stops = st.multiselect('Select Stops:', options=filtered_stops['Denominació / Denominación'].unique())

    # Filtrar datos en función de las paradas seleccionadas
    filtered_data_stops = filtered_stops[filtered_stops['Denominació / Denominación'].isin(selected_stops)]

    # Verificar si hay datos para mostrar
    if not filtered_data_stops.empty:
        # Agregar datos de ícono a los datos filtrados
        filtered_data_stops['icon_data'] = filtered_data_stops.apply(lambda row: {
            'url': 'https://cdn-icons-png.flaticon.com/128/3176/3176278.png',
            'width': 128,
            'height': 128,
            'anchorY': 128,
        }, axis=1)

        # Definir el estado inicial del mapa
        view_state = pdk.ViewState(
            latitude=filtered_data_stops['lat'].mean(),
            longitude=filtered_data_stops['lon'].mean(),
            zoom=12,
            pitch=50
        )

        # Definir la capa de íconos
        icon_layer = pdk.Layer(
            'IconLayer',
            data=filtered_data_stops,
            get_icon='icon_data',
            get_size=2.5,
            size_scale=15,
            get_position='[lon, lat]',
            pickable=True,
            auto_highlight=True
        )

        # Crear el mapa con vista satelital
        map = pdk.Deck(
            layers=[icon_layer],
            initial_view_state=view_state,
            map_style='mapbox://styles/mapbox/satellite-v9',
            tooltip={"text": "{Denominació / Denominación}\nBuses: {Línies / Líneas}"}
        )

        st.pydeck_chart(map)
    else:
        st.write("No data available for the selected stops.")

elif pagina == 'ValenBici':
    
        
    API_KEY = 'e70c46dec74a2ec4923ed1ce7255e8c1d6ccec7f'
    CONTRACT_NAME = 'Valence'  # Revisa el nombre de contrato para confirmar que es correcto
    
    def load_data():
        url = f"https://api.jcdecaux.com/vls/v1/stations?contract={CONTRACT_NAME}&apiKey={API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            stations = response.json()
            data = pd.json_normalize(stations)
            # Importante: Renombrar correctamente las columnas según la salida de la API
            if 'position.lat' in data.columns and 'position.lng' in data.columns:
                data.rename(columns={'position.lat': 'lat', 'position.lng': 'lon'}, inplace=True)
            return data
        else:
            print("Failed to retrieve data:", response.status_code)
            return pd.DataFrame()  # Retorna un DataFrame vacío si hay un error
    
    data = load_data()
    
    # Crear datos de íconos dentro de la función de carga para asegurar su disponibilidad
    data['icon_data'] = [{
        "url": "https://img.icons8.com/emoji/48/000000/bicycle-emoji.png",
        "width": 128,
        "height": 128,
        "anchorY": 128,
    }] * len(data)
    
    st.image('234.jpg')
    st.title('Route Duration')
    
    st.markdown("""
### Welcome to our interactive ValenBici tool!

 Here’s how you can use our application to calculate the estimated travel time between two bicycle stations in Valence. This step-by-step guide will help you make the most of the service, ensuring that you can plan your trips efficiently within the free time limit.
""")
    
    
    # Buscador para la primera parada
    search_text1 = st.sidebar.text_input("Search Stop 1:")
    if search_text1:
        filtered_data1 = data[data['address'].str.contains(search_text1, case=False)]
    else:
        filtered_data1 = data
    
    # Buscador para la segunda parada
    search_text2 = st.sidebar.text_input("Search Stop 2:")
    if search_text2:
        filtered_data2 = data[data['address'].str.contains(search_text2, case=False)]
    else:
        filtered_data2 = data
    
    # Ordenar las paradas filtradas
    filtered_data1 = filtered_data1.sort_values('address')
    filtered_data2 = filtered_data2.sort_values('address')
    
    # Seleccionar dos paradas
    parada1 = st.sidebar.selectbox("Stop 1", filtered_data1['address'])
    parada2 = st.sidebar.selectbox("Stop 2", filtered_data2['address'])
    
    # Obtener coordenadas de las paradas seleccionadas
    coords1 = data[data['address'] == parada1][['lon', 'lat']].values[0]
    coords2 = data[data['address'] == parada2][['lon', 'lat']].values[0]
    
    # Filtrar los datos para mostrar solo las estaciones seleccionadas
    selected_stations = data[data['address'].isin([parada1, parada2])]
    
    # Configurar la API de Mapbox
    MAPBOX_API_KEY = 'sk.eyJ1IjoibXJvY3ZhbDAxOCIsImEiOiJjbHdxb2YzbnQwNHkxMmlzN3FiYjhmdjM2In0.OMAngKqcq66vxUyM8MeKWw'
    
    # Obtener la ruta y tiempo estimado entre las paradas usando la API de Mapbox Directions
    def get_route_time(coords1, coords2, api_key):
        url = f"https://api.mapbox.com/directions/v5/mapbox/cycling/{coords1[0]},{coords1[1]};{coords2[0]},{coords2[1]}"
        params = {
            "access_token": api_key,
            "geometries": "geojson"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            route = data['routes'][0]['geometry']
            duration = data['routes'][0]['duration'] / 60  # Convertir a minutos
            return route, duration
        else:
            return None, None
    
    if st.sidebar.button("Calculate Route"):
        route, duration = get_route_time(coords1, coords2, MAPBOX_API_KEY)
        if route:
            st.sidebar.write(f"Estimated time: {duration:.2f} minutos")
    
            # Añadir la ruta al mapa
            route_layer = pdk.Layer(
                "PathLayer",
                data=pd.DataFrame([{"path": route['coordinates']}]),
                get_path="path",
                get_width=5,
                get_color=[255, 0, 0],
                width_min_pixels=2
            )
    
            # Configuración del mapa con estaciones seleccionadas
            view_state = pdk.ViewState(
                latitude=(coords1[1] + coords2[1]) / 2,
                longitude=(coords1[0] + coords2[0]) / 2,
                zoom=13,
                pitch=0
            )
    
            icon_layer = pdk.Layer(
                "IconLayer",
                selected_stations,
                get_icon='icon_data',
                get_position='[lon, lat]',
                size_scale=15,
                get_size=4,
                get_color=[255, 165, 0],
                pickable=True
            )
    
            st.pydeck_chart(pdk.Deck(
                layers=[icon_layer, route_layer],
                initial_view_state=view_state,
                map_style='mapbox://styles/mapbox/light-v9',
                tooltip={
                    "html": "<b>Address:</b> {address}<br/>"
                            "<b>Bikes Available:</b> {available_bikes}<br/>"
                            "<b>Free Spaces:</b> {available_bike_stands}<br/>"
                            "<b>Status:</b> {status}",
                    "style": {
                        "backgroundColor": "steelblue",
                        "color": "white"
                    }
                }
            ))
        else:
            st.sidebar.write("The route could not be calculated. Please try again.")
    
    # Mostrar el mapa inicial con todas las estaciones
    else:
        view_state = pdk.ViewState(
            latitude=data['lat'].mean(),
            longitude=data['lon'].mean(),
            zoom=13,
            pitch=0
        )
    
        icon_layer = pdk.Layer(
            "IconLayer",
            data,
            get_icon='icon_data',
            get_position='[lon, lat]',
            size_scale=15,
            get_size=4,
            get_color=[255, 165, 0],
            pickable=True
        )
    
        st.pydeck_chart(pdk.Deck(
            layers=[icon_layer],
            initial_view_state=view_state,
            map_style='mapbox://styles/mapbox/light-v9',
            tooltip={
                "html": "<b>Address:</b> {address}<br/>"
                        "<b>Bikes Available:</b> {available_bikes}<br/>"
                        "<b>Free Spaces:</b> {available_bike_stands}<br/>"
                        ,"<b>Status:</b> {status}"
                "style": {
                    "backgroundColor": "steelblue",
                    "color": "white"
                }
            }
        ))

    
    st.markdown("""
    ### User Guide: ValenBici Route Time Calculator
    
#### Step 1: Access the Tool

Simply visit our page on the Streamivyt app. The data you will use is updated every minute to ensure accuracy.

#### Step 2: Select Your Stations

In the sidebar, you will find two search fields:

	•	Search Stop 1: Here you can type and select your starting station.
	•	Search Stop 2: Here you can type and select your destination station.

As you begin to type, the app will display the matching options, making it easy to select.

#### Step 3: Calculate the Route

Once both stations are selected, press the Calculate Route button. Our application will use the Mapbox Directions API to calculate the optimal route and provide you with the estimated biking time.

#### Step 4: View the Route on the Map

After calculating the route:

	•	The estimated travel time will be displayed in the sidebar.
	•	On the main map, you will see the route marked in red, along with bicycle icons representing the selected stations.

#### Step 5: Continuous Planning

You don’t need to do anything else to keep the information updated. The page will automatically refresh every 60 seconds, ensuring that the information you see is always the latest. This is ideal for keeping your plans up to date without any additional effort.

#### Additional Tips

	•	Use the search function to quickly find your favorite stations.
	•	Plan your trips according to the estimated time to maximize the use of the free 30-minute period provided by the annual pass.

We hope this tool is extremely useful for your daily commutes in Valence! With ValenBici, getting around the city has never been so easy and convenient.
    
    """) 
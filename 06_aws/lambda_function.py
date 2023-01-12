#built-in libs
import json
from pytz import timezone
from datetime import datetime, date, timedelta

# External libs(layers)
import requests
import sqlalchemy

import pandas as pd
import numpy as np


# own modules
import keys

## Static functions ##
#---------------------#
def get_MySQL_con():
    schema="gans_db"
    host="wbs-gans-db.c87binzvwbjx.eu-central-1.rds.amazonaws.com"
    user="admin"
    password=keys.SQL_PASSWORD
    port=3306
    con = f'mysql+pymysql://{user}:{password}@{host}:{port}/{schema}'
    return con
#------------------------------------------------------#
# Global Var
CONN = get_MySQL_con()
#------------------------------------------------------#
def lambda_handler(event, context):
    
    # retrieve city_df
    city_df =  pd.read_sql_table('city',con=CONN)
    #update weather table
    weather_dict = get_cityWeather(city_df)
    weather_df = pd.DataFrame(weather_dict)
    weather_df.to_sql('weather',if_exists='append',con=CONN,index=False)
    
    # retrieve airport_df
    airport_df  =  pd.read_sql_table('airport',con=CONN)
    #update flight table
    flights_df_l = get_flights(airport_df)
    flights_df   = pd.DataFrame(flights_df_l)
    flights_df.to_sql('flight',if_exists='append',con=CONN,index=False)
    return {
        'statusCode': 200,
        'body': json.dumps('All done well!')}
#------------------------------------------------------#   

  
#------------------------------------------------------#
def get_cityWeather(city_df): 
    cities_weath = {"city_id":[]
                    ,"forcast_time":[]
                    ,"outlook":[]
                    ,"temperature":[]
                    ,"feels_like":[]
                    ,"wind_speed":[]
                    ,"rain_prob":[]
                    }
    for i in range(len(city_df)):
        lat=city_df.lat[i]
        lon=city_df.lon[i]
        url_weather= f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={keys.Weather_API_key}&units=metric"
        weather_response = requests.get(url_weather)
        weather_response.raise_for_status()

        city_json = weather_response.json()
        #API interface provide weather forcast for the next 5 days(per 3 hours)
        #iterate = math.ceil(RERUN_TIME_IN_HOURS/WEATHER_FORCAST_TIMEWINDOW)
        iterate = 8
        for forcast in city_json["list"][:iterate]:
            cities_weath["city_id"].append(city_df.city_id[i])
            cities_weath["forcast_time"].append(forcast.get('dt_txt', pd.NaT))
            cities_weath["temperature"].append(forcast["main"].get('temp', np.NaN))
            cities_weath["outlook"].append(forcast["weather"][0].get('description', "unknown"))
            cities_weath["feels_like"].append(forcast["main"].get('feels_like', np.NaN))
            cities_weath["wind_speed"].append(forcast["wind"].get('speed', np.NaN))
            cities_weath["rain_prob"].append(forcast.get('pop', np.NaN))
    return cities_weath
#------------------------------------------------------#
def get_flights(airports_df):
    # Prepare URL inputs
    today = datetime.now().astimezone(timezone('Europe/Berlin')).date()
    #rerun_window = math.ceil(RERUN_TIME_IN_HOURS/24) #roundup to bigger integer
    next_run = (today + timedelta(days=1))
    times = [["00:00","11:59"],["12:00","23:59"]]
    
    flight_df_l = []
    #Loop over all airports
    #TODO when sure remove [1:2] to loop over all airports
    for icao in airports_df.icao[1:2]:
        for time in times:
            url = f"https://aerodatabox.p.rapidapi.com/flights/airports/icao/{icao}/{next_run}T{time[0]}/{next_run}T{time[1]}"
            querystring = {"withLeg":"true","direction":"Arrival","withCancelled":"false","withCodeshared":"true","withCargo":"false","withPrivate":"false","withLocation":"false"}
            headers = {
				"X-RapidAPI-Key": keys.Flight_API_key,
				"X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
			}
            response = requests.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            flights_12h_json = response.json()
            for flight in flights_12h_json["arrivals"]:
                flight_dict = {}
                flight_dict['arrival_icao']         = icao
                flight_dict["arrival_time_local"]   = flight["arrival"].get('scheduledTimeLocal', pd.NaT)
                flight_dict["arrival_terminal"]     = flight['arrival'].get('terminal', "unknown")
                flight_dict["departure_city"]       =  flight["departure"]["airport"].get("name", "unknown")
                flight_dict["departure_icao"]       =  flight["departure"]["airport"].get("icao", "unknown")
                flight_dict["departure_time_local"] = flight["departure"].get("scheduledTimeLocal", pd.NaT)
                flight_dict["airline"]              =  flight["airline"].get("name", "unknown")
                flight_dict["flight_number"]        =  flight.get("number", "unknown")
                flight_dict["data_retrieved_on"]    =  datetime.now().astimezone(timezone('Europe/Berlin')).date()
                flight_df_l.append(flight_dict)
    return flight_df_l


    
import requests
import pandas as pd
import re
import numpy as np
from functools import lru_cache

URL = "https://mosmap.ru/api/api_analitic.php"
URL_GEO = "https://mosmap.ru/api/api_geocoder.php"
API_KEY = "b089de13-5470-4717-9d5f-425f2b4b41a8"

def api_call_geocoder_address(address):
    params = {
        'apikey': API_KEY,
        'address': address
    }
    response = requests.get(URL_GEO, params=params)
    data = response.json()
    return data

def api_call_geocoder_coo(lat, lon):
    params = {
        'apikey': API_KEY,
        'longitude': lon,
        'latitude': lat,
    }
    response = requests.get(URL_GEO, params=params)
    data = response.json()
    return data

def api_call_analytic(lat, lon, radius):
    params = {
        'apikey': API_KEY,
        'longitude': lon,
        'latitude': lat,
        'radius': radius
    }
    
    response = requests.get(URL, params=params)
    data = response.json()
    return data

needed_keys = [
    'latitude', 'longitude',
    'district_name', # название района
    'price', #
    'orgs', # количество организаций
    'zone', # Информация по жилой зоне вокруг точки
    'bcenters', # Расстояние до ближайших бизнес-центров (в метрах) (нужно агрегировать)
    'metro_exits', # Выходы метро и координаты до него
    'traffic1', 'traffic2', 'traffic3', 'traffic4' # 4 типа трафика
]

@lru_cache(maxsize=2048)
def get_data_geocoder_coo(lat, lon):
    data = api_call_geocoder_coo(lat, lon)
    return {
        'lat': data['latitude'],
        'lon': data['longitude'],
        'long_address': data['long_address'],
        'near_subway_distance': data['near_subway_distance'],
    }

@lru_cache(maxsize=2048)
def get_data_geocoder_address(address):
    data = api_call_geocoder_address(address)
    return {
        'lat': data['latitude'],
        'lon': data['longitude'],
        'long_address': data['long_address'],
        'near_subway_distance': data['near_subway_distance'],
    }

@lru_cache(maxsize=2048)
def get_data_radius(lat, lon, radius):
    data = api_call_analytic(lat, lon, radius)

    # Организации: количество вокруг
    orgs = [d for d in data["orgs"].values()]
    orgs_dict = {f"{d['group_name']}_count_{radius}m": d['count'] for d in orgs}

    # Зона: информация о недвижимости вокруг
    zone_info = {d['name']: d['value'] for d in data["zone"]}
    if 'Строений' not in zone_info:
        n_buildings = None
    else:
        n_buildings = zone_info['Строений']
    if 'Жилых домов' not in zone_info:
        n_living_buildings = None
    else:
        n_living_buildings = zone_info['Жилых домов']
    if 'Квартир' not in zone_info:
        n_flats = None
    else:
        n_flats = zone_info['Квартир']

    # Бизнес-центры -- расстояния
    bc_distances = [d['distance'] for d in data["bcenters"]]
    min_bc_distance = np.min(bc_distances)
    mean_bc_distance = np.mean(bc_distances)

    pd_dict = {
        'district_name': data['district_name'],
        
        f'n_buildings_{radius}m': n_buildings,
        f'n_living_buildings_{radius}m': n_living_buildings,
        f'n_flats_{radius}m': n_flats,

        f'min_bc_distance_{radius}m': min_bc_distance,
        f'mean_bc_distance_{radius}m': mean_bc_distance,

        f'traffic1_{radius}m': data['traffic1'],
        f'traffic2_{radius}m': data['traffic2'],
        f'traffic3_{radius}m': data['traffic3'],
        f'traffic4_{radius}m': data['traffic4'],
    }

    pd_dict.update(data["price"]) # Не зависит от радиуса
    pd_dict.update(orgs_dict)
    return pd_dict
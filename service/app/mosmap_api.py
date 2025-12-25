import os
import re
import requests
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from functools import lru_cache

assert load_dotenv()

URL = os.getenv("MOSMAP_URL")
URL_GEOCODER = os.getenv("MOSMAP_URL_GEOCODER")
API_KEY = os.getenv("MOSMAP_API_KEY")

'''
Модуль получения геоданных через mosmap
========================================
NEEDED_KEYS = [
    'latitude', 'longitude',
    'district_name', # название района
    'price', #
    'orgs', # количество организаций
    'zone', # Информация по жилой зоне вокруг точки
    'bcenters', # Расстояние до ближайших бизнес-центров (в метрах) (нужно агрегировать)
    'metro_exits', # Выходы метро и координаты до него
    'traffic1', 'traffic2', 'traffic3', 'traffic4' # 4 типа трафика
]
'''


def api_call_geocoder_address(address):
    params = {
        'apikey': API_KEY,
        'address': address
    }
    response = requests.get(URL_GEOCODER, params=params)
    data = response.json()
    return data


def api_call_geocoder_coo(lat, lon):
    params = {
        'apikey': API_KEY,
        'longitude': lon,
        'latitude': lat,
    }
    response = requests.get(URL_GEOCODER, params=params)
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


@lru_cache(maxsize=2048)
def get_data_geocoder_coo(lat, lon):
    data = api_call_geocoder_coo(lat, lon)
    return {
        'lat': data['latitude'],
        'lon': data['longitude'],
        'long_address': data['long_address'],
        'near_subway_distance': data['near_subway_distance'],
    }


def get_and_check_i_dont_want_to_make_names(d: dict, id):
    if not (type(d) is dict):
        return np.nan
    if id not in d:
        return np.nan
    return d[id]


@lru_cache(maxsize=2048)
def get_data_radius(lat, lon, radius):
    data = api_call_analytic(lat, lon, radius)

    # Организации: количество вокруг
    orgs = {(d['group_name']+f"_{radius}"): d['count'] 
            for d in get_and_check_i_dont_want_to_make_names(data, "orgs").values()}

    # Зона: информация о недвижимости вокруг
    if type(get_and_check_i_dont_want_to_make_names(data, "zone")) is list:
        zone_info = {get_and_check_i_dont_want_to_make_names(d, "name"): get_and_check_i_dont_want_to_make_names(d, "value") 
                    for d in get_and_check_i_dont_want_to_make_names(data, "zone")}
    else:
        zone_info = np.nan
    n_buildings = get_and_check_i_dont_want_to_make_names(zone_info, 'Строений')
    n_living_buildings = get_and_check_i_dont_want_to_make_names(zone_info, 'Жилых домов')
    n_flats = get_and_check_i_dont_want_to_make_names(zone_info, 'Квартир')

    # Бизнес-центры -- расстояния
    if type(get_and_check_i_dont_want_to_make_names(data, "bcenters")) is list:
        bc_distances = [get_and_check_i_dont_want_to_make_names(d, 'distance')
                        for d in get_and_check_i_dont_want_to_make_names(data, "bcenters")]
    else:
        bc_distances = []
    bc_distances = np.array(bc_distances)
    if len(bc_distances) != 0:
        min_bc_distance = np.min(bc_distances)
        mean_bc_distance = np.mean(bc_distances)
    else:
        min_bc_distance = None
        mean_bc_distance = None

    pd_dict = {
        'district_name': get_and_check_i_dont_want_to_make_names(data, 'district_name'),
        
        f'n_buildings_{radius}m': n_buildings,
        f'n_living_buildings_{radius}m': n_living_buildings,
        f'n_flats_{radius}m': n_flats,

        f'min_bc_distance_{radius}m': min_bc_distance,
        f'mean_bc_distance_{radius}m': mean_bc_distance,

        f'traffic1_{radius}m': get_and_check_i_dont_want_to_make_names(data, 'traffic1'),
        f'traffic2_{radius}m': get_and_check_i_dont_want_to_make_names(data, 'traffic2'),
        f'traffic3_{radius}m': get_and_check_i_dont_want_to_make_names(data, 'traffic3'),
        f'traffic4_{radius}m': get_and_check_i_dont_want_to_make_names(data, 'traffic4'),
    }

    # pd_dict.update(data["price"]) # Не зависит от радиуса
    pd_dict.update(orgs)
    pd_dict.update({'district_price': get_and_check_i_dont_want_to_make_names(
        get_and_check_i_dont_want_to_make_names(data, 'price'), 'district_price')
    })
    return pd_dict


async def get_mosmap_data(lat: float, lon: float, radius: int) -> pd.DataFrame | None:
    try:
        data_dict = get_data_radius(lat, lon, radius)
        return pd.DataFrame(data=data_dict, index=[0])
    except BaseException as ex:
        print(ex)
        return None

import os
import re
import requests
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from functools import lru_cache

assert load_dotenv()

URL = os.getenv("YANDEX_BASE_URL")

YANDEX_RUBRICS = [
	[],
	...
]

async def get_yandex_data(lat: float, lon: float, radius: int):
	params = {
        'lat': lat,
        'lon': lon,
        'radius': radius,
        'rubrics': YANDEX_RUBRICS,
    }
    
    try:
    	response = requests.get(f"{URL}/get_yandex", params=params)
    	response.raise_for_status()
    	data = response.json()["data"]
    	return pd.DataFrame(data=data, index=[0])

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса /get_yandex: {e}")
        return None

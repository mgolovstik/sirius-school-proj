import os
import requests
import pandas as pd
from dotenv import load_dotenv

assert load_dotenv()

URL = os.getenv("YANDEX_BASE_URL")

YANDEX_RUBRICS = [
	[],
	...
]

async def get_yandex_data(lat: float, lon: float, radius: int, rubrics: list = None):
    json_data = {
        'lat': lat,
        'lon': lon,
        'radius': radius,
        'rubrics': YANDEX_RUBRICS if rubrics is None else rubrics,
    }

    try:
        response = requests.get(f"{URL}/get_yandex", json=json_data)
        response.raise_for_status()
        data = response.json()["data"]
        return pd.DataFrame(data=data, index=[0])
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса /get_yandex: {e}")
        return None

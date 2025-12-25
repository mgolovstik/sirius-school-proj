import mlflow
import asyncio
import pandas as pd
from dotenv import load_dotenv
from mosmap_api import get_mosmap_data
from yandex_api import get_yandex_data

assert load_dotenv()


CHOSEN_COLUMNS = [
	...
]


def to_pandas(raw_json):
	df_point = pd.DataFrame(data=raw_json, index=[0])
	return df_point


def predict_ad(raw_json):
	lat, lon = raw_json["lat"], raw_json["lon"]
	df_point = to_pandas(raw_json)

	mosmap_data_1, mosmap_data_2, yandex_data_1, yandex_data_2 = await asyncio.gather(
		get_mosmap_data(lat, lon, 300),
		get_mosmap_data(lat, lon, 600),
		get_yandex_data(lat, lon, 300, YANDEX_CATEGORIES),
		get_yandex_data(lat, lon, 600, YANDEX_CATEGORIES),
	)

	mosmap_data_2 = mosmap_data_2.drop(['district_price', 'district_name'], axis=1)
	mosmap_data = pd.concat([mosmap_data_1, mosmap_data_2], axis=1)
	yandex_data = pd.concat([yandex_data_1, yandex_data_2], axis=1)

	df_point = pd.concat([df_point, mosmap_data, yandex_data])

	model = mlflow.sklearn.load_model("models:/moscow-rent/Production")
	y_pred = model.predict(df_point[CHOSEN_COLUMNS])[0]

	... # TODO
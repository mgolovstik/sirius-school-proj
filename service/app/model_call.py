import mlflow
import asyncio
import pandas as pd
from dotenv import load_dotenv
from app.mosmapapi import get_mosmap_data
from yb.main import get_yandex
from yb.schemas import YandexBaseInput, YandexBaseOutput

assert load_dotenv()

YANDEX_CATEGORIES = [
	"cnt_Бизнес-центр",
    "cnt_Ресторан",
    "cnt_Караоке-клуб",
    "cnt_Кондитерская",
    "cnt_Магазин_цветов",
    "cnt_Банк",
    "cnt_Кофейня"
]

CHOSEN_COLUMNS = [
	"Общая площадь", "Расстояние до метро, км", "Этаж", "Вид объекта",
	"district_price",
    "traffic4_300m",
    "n_buildings_600m",
    "traffic1_600m",
    "n_buildings_300m",
	"district_name",
	"cnt_Бизнес-центр",
    "cnt_Ресторан",
    "cnt_Караоке-клуб",
    "cnt_Кондитерская",
    "cnt_Магазин_цветов",
    "cnt_Банк",
    "cnt_Кофейня"
]

async def get_yandex_data(lat, lon, radius, rubrics):
	return await get_yandex(YandexBaseInput(lat=lat, lon=lon, radius=radius, rubrics=rubrics))

def to_pandas(raw_json):
	df_point = pd.DataFrame(data=raw_json, index=[0])
	return df_point


async def predict_ad(raw_json):
	lat, lon = raw_json["lat"], raw_json["lon"]
	df_point = to_pandas(raw_json)

	mosmap_data_1 = await get_mosmap_data(lat, lon, 300)
	mosmap_data_2 = await get_mosmap_data(lat, lon, 600).drop(['district_price', 'district_name'], axis=1)
	yandex_data_1 = await get_yandex_data(lat, lon, 300, YANDEX_CATEGORIES)
	yandex_data_2 = await get_yandex_data(lat, lon, 600, YANDEX_CATEGORIES)

	mosmap_data = pd.concat([mosmap_data_1, mosmap_data_2], axis=1)
	yandex_data = pd.concat([yandex_data_1, yandex_data_2], axis=1)

	df_point = pd.concat([df_point, mosmap_data, yandex_data])

	mlflow_model = mlflow.sklearn.load_model("models:/" + "misha-test-model" + "/3")
	y_pred = mlflow_model.predict(df_point[CHOSEN_COLUMNS])[0]

	return y_pred
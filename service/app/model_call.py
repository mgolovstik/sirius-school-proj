import asyncio
import pandas as pd
from dotenv import load_dotenv
from app.mosmapapi import get_mosmap_data
from yb.main import get_yandex
from yb.schemas import YandexBaseInput, YandexBaseOutput
from var import mlflow_model, data_transformer

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
	"Общая площадь",
	"Расстояние до метро, км",
	"Этаж",
	"Вид объекта",
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

RESULT_COLUMNS = [
	'Общая площадь', 
	'district_name', 
	'district_price', 
	'cnt_Ресторан', 
	'traffic4_300m', 
	'Этаж', 
	'cnt_Банк', 
	'n_buildings_600m', 
	'cnt_Бизнес-центр', 
	'cnt_Кофейня', 
	'cnt_Караоке-клуб', 
	'traffic1_600m', 
	'n_buildings_300m', 
	'cnt_Кондитерская', 
	'cnt_Магазин_цветов', 
	'Расстояние до метро, км', 
	'Вид объекта_Торговое / Свободного назначения',
	'Вид объекта_Офисное помещение'
]

async def get_yandex_data(lat, lon, radius, rubrics):
	return await get_yandex(YandexBaseInput(lat=lat, lon=lon, radius=radius, rubrics=rubrics))

def to_pandas(raw_json):
	df_point = pd.DataFrame(data=raw_json, index=[0])
	return df_point


async def predict_ad(raw_json):
	global mlflow_model
	global data_transformer

	lat, lon = raw_json["lat"], raw_json["lon"]
	df_point = to_pandas(raw_json)
	df_point.rename(columns={
		'square': 'Общая площадь',
		'floor': 'Этаж',
		'metro_dist': 'Расстояние до метро, км',
		'object_type': "Вид объекта"
	}, inplace=True)
	
	mosmap_data_1 = await get_mosmap_data(lat, lon, 300)
	mosmap_data_2 = (await get_mosmap_data(lat, lon, 600)).drop(['district_price', 'district_name'], axis=1)
	
	yandex_data = (await get_yandex_data(lat, lon, 600, YANDEX_CATEGORIES)).model_dump()['data']
	print(yandex_data)

	mosmap_data = pd.concat([mosmap_data_1, mosmap_data_2], axis=1)
	yandex_data = pd.DataFrame(yandex_data, index=[0])
	print(yandex_data)
	df_point = pd.concat([df_point, mosmap_data, yandex_data], axis=1)
	print(df_point)
	df_point = data_transformer.transform(df_point[CHOSEN_COLUMNS])
	print(df_point)

	y_pred = mlflow_model.predict(df_point[RESULT_COLUMNS])[0]

	return y_pred
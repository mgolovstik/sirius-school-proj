from fastapi import FastAPI
from yb.yandex_geo import get_yandex_data
from yb.schemas import YandexBaseInput, YandexBaseOutput

app = FastAPI()

@app.get("/get_yandex")
async def get_yandex(input_json: YandexBaseInput) -> YandexBaseOutput | None:
    raw_json = input_json.model_dump()
    data = await get_yandex_data(**raw_json)
    data = data.to_dict(orient='records')[0]
    print(data)
    return YandexBaseOutput(data=data)

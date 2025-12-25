from fastapi import FastAPI
from yandex_geo import get_dict
from schemas import YandexBaseInput, YandexBaseOutput


app = FastAPI()


@app.post("/get_yandex")
async def get_yandex(input_json: YandexBaseInput) -> YandexBaseOutput | None:
    raw_json = input_json.model_dump()
    try:
        data = get_dict(raw_json)
        result_dict = {
            'data': data,
        }
        return YandexBaseOutput(**result_dict)
    except Exception as e:
        print(f"Failed with exception:\n{str(e)}")

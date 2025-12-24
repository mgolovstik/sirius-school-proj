from fastapi import FastAPI
from yandex_base.yandex_geo import get_list
from schemas import YandexBaseInput, YandexBaseOutput


app = FastAPI()


@app.post("/yandex_base")
async def (input_json: YandexBaseInput) -> YandexBaseOutput | None:
    raw_json = input_json.model_dump()
    try:
        data = get_list(raw_json)
        result_dict = {
            'data': data,
        }
        return YandexBaseOutput(**result_dict)
    except Exception as e:
        print(f"Failed with exception:\n{str(e)}")

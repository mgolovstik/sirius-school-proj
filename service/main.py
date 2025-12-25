from fastapi import FastAPI
from app.model_call import predict_ad
from schemas import AdvertInput, AdvertOutput

app = FastAPI(docs_page="/docs")

@app.post("/predict")
async def predict(input_json: AdvertInput) -> AdvertOutput | None:
	raw_json = input_json.model_dump()
	result_json = await predict_ad(raw_json)
	return AdvertOutput(pred=float(result_json))

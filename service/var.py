import os
import mlflow
from dotenv import load_dotenv
import joblib

assert load_dotenv()

URL = os.getenv("MOSMAP_URL")
URL_GEOCODER = os.getenv("MOSMAP_GEOCODER_URL")
API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv('BOT_TOKEN')

mlflow_model = mlflow.sklearn.load_model("models:/" + "misha-test-model" + "/5")
data_transformer = joblib.load("transformer.joblib")
FROM python:3.10-bullseye

RUN pip install mlflow==2.10.0

COPY . .

EXPOSE 5020

CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5020"]
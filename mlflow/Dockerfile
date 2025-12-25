FROM python:3.10-bullseye

RUN pip install mlflow==2.1.1

COPY . .

EXPOSE 5000

CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]
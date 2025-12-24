FROM python:3.10-bullseye

RUN apt-get -y update

WORKDIR machine

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5005"]
FROM python:3.8.5

RUN mkdir /code

COPY requirements.txt /code
COPY .flaskenv /code

RUN pip install -r /code/requirements.txt

COPY . /code
WORKDIR /code
EXPOSE 8888

CMD ["gunicorn", "-b", "localhost:8888", "spotify_auth:app"]



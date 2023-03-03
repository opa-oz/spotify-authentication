FROM python:3.8.5

WORKDIR /code

COPY requirements.txt /code
RUN pip install -r /code/requirements.txt

COPY .flaskenv /code

COPY . /code
EXPOSE 8888

CMD ["gunicorn", "-b", "0.0.0.0:8888", "spotify_auth:app"]



import random
import os
import base64
from flask import request, redirect, make_response, Response, render_template
from flask_cors import CORS, cross_origin
from urllib.parse import urlencode
import requests

from app import app

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
callback_url = os.environ.get('CALLBACK_URL')
state_key = 'spotify_auth_state'
scope = 'user-read-private user-read-email playlist-modify-public playlist-modify-private'
state_length = 16
redirect_uri = f'{callback_url}/callback'
spotify_token_url = 'https://accounts.spotify.com/api/token'


@app.route('/')
@app.route('/index')
@app.route('/ping')
@cross_origin()
def index():
    return render_template('index.html')


def generate_random_string(length=state_length):
    possible_symbols = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(possible_symbols) for i in range(length))


@app.route('/tokens')
@cross_origin()
def show_tokens():
    args = request.args
    return {'access_token': args.get('access_token'), 'refresh_token': args.get('refresh_token')}


@app.route('/login')
@cross_origin()
def login():
    state = generate_random_string(state_length)
    query_params = urlencode({'response_type': 'code',
                              'client_id': client_id,
                              'scope': scope,
                              'redirect_uri': redirect_uri,
                              'state': state
                              })

    response = make_response(redirect(f'https://accounts.spotify.com/authorize?{query_params}'))
    response.set_cookie(f'{state_key}', state)
    return response


@app.route('/callback')
@cross_origin()
def callback():
    query_params = request.args
    code = query_params.get('code')
    state = query_params.get('state')
    stored_state = request.cookies.get(f'{state_key}')
    print({'state': state, 'stored_state': stored_state})
    if not state or state != stored_state:
        return Response('state mismatch', status=400, )

    auth_client = f'{client_id}:{client_secret}'
    auth_encode = 'Basic ' + base64.b64encode(auth_client.encode()).decode()
    auth_headers = {
        'Authorization': auth_encode,
    }
    data = {
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'code': code
    }

    token_response = requests.post(spotify_token_url, data=data, headers=auth_headers)
    if token_response.status_code != 200:
        return {'status_code': token_response.status_code, 'message': token_response.json()}
    access_token = token_response.json().get('access_token')
    refresh_token = token_response.json().get('refresh_token')

    res = make_response(redirect(f'tokens?access_token={access_token}&refresh_token={refresh_token}'))
    return res


@app.route('/refresh_token')
@cross_origin()
def refresh_token():
    refresh_token = request.args.get('refresh_token')
    if not refresh_token:
        return {'error': 400, 'message': 'no refresh_token provided'}
    auth_client = f'{client_id}:{client_secret}'
    auth_encode = 'Basic ' + base64.b64encode(auth_client.encode()).decode()
    auth_headers = {
        'Authorization': auth_encode,
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }

    refresh_token_response = requests.post(spotify_token_url, data=data, headers=auth_headers)
    if refresh_token_response.status_code != 200:
        return {'status_code': refresh_token_response.status_code, 'message': refresh_token_response.json()}

    return {'access_token': refresh_token_response.json().get('access_token')}

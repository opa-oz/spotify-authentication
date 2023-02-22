import random
import os
import base64
from flask import request, redirect, make_response, Response
from urllib.parse import urlencode
import requests

from app import app

client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')
state_key = 'spotify_auth_state'
scope = 'user-read-private user-read-email playlist-modify-public playlist-modify-private'
state_length = 16
redirect_uri = 'http://localhost:8888/callback'
spotify_token_url = 'https://accounts.spotify.com/api/token'


@app.route('/')
@app.route('/index')
@app.route('/ping')
def index():
    return 'server running'


def generate_random_string(length=state_length):
    possible_symbols = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(possible_symbols) for i in range(length))


@app.route('/tokens')
def show_tokens():
    args = request.args
    return {'access_token': args.get('access_token'), 'refresh_token': args.get('refresh_token')}


@app.route('/login')
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
def callback():
    query_params = request.args
    code = query_params.get('code')
    state = query_params.get('state')
    stored_state = request.cookies.get(f'{state_key}')
    print({'state': state, 'stored_state': stored_state})
    if not state or state != stored_state:
        return Response('state mismatch', status=400, )
    # resp = make_response('http://localhost:8888/callback')
    # resp.delete_cookie('lol')

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

    # headers = {'Authorization': f'Bearer {access_token}'}
    # access_api = requests.get('https://api.spotify.com/v1/me', headers=headers)
    # if access_api.status_code != 200:
    #     return {'error': access_api.status_code, 'message': access_api.json()}
    res = make_response(redirect(f'tokens?access_token={access_token}&refresh_token={refresh_token}'))
    return res

@app.route('/refresh_token')
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
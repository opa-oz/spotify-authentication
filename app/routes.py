import random
import os
from flask import request, redirect, make_response
from urllib.parse import urlencode
from app import app

client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')
state_key = 'spotify_auth_state'
scope = 'user-read-private user-read-email playlist-modify-public playlist-modify-private'
state_length = 16
redirect_uri = 'http://localhost:8888/callback'


@app.route('/')
@app.route('/index')
@app.route('/ping')
def index():
    return 'server running'


@app.route('/test')
def generate_random_string(length=state_length):
    possible_symbols = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(possible_symbols) for i in range(length))


@app.route('/login')
def login():
    state = generate_random_string(state_length)
    query_params = urlencode({'response_type': 'code',
                              'client_id': client_id,
                              'scope': scope,
                              'redirect_uri': redirect_uri,
                              'state': 'state'
                              })

    response = make_response(redirect(f'https://accounts.spotify.com/authorize?{query_params}'))
    response.set_cookie(f'{state_key}', state)
    return response


@app.route('/callback')
def callback():
    return 'callback success'

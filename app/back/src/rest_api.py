#!/usr/bin/env python
# -*- coding: utf-8 -*-
# rest_api.py
import os

from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import json
import psycopg2
import requests
from contextlib import closing

from src.config import config
import src.connect_pg as connect_pg
import src.apiException as apiException
from datetime import timedelta
from src.routes.user_route import user

app = Flask(__name__)
"""JWT CONFIGURATION"""

secret_key = os.urandom(32)
app.config['SECRET_KEY'] = secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)

jwt = JWTManager(app)


"""Register blueprints"""
app.register_blueprint(user)

"""Variable représentant l'application web"""

cors = CORS(app, resources={r"*": {"origins": "*"}})

api = Api(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


def create_app(config):
    """Cette fonction crée l'application

    :param config: définit les options souhaité
    :type config: Objet
    
    :return:  l'application configurer
    :rtype: flask.app.Flask
    """
    
    app.config.from_object(config)
    return app
    
@app.route('/index')
def index():
    """
    Cette fonction permet de pinger l'application, elle sert de route Flask à l'adresse '/index'

    :return:  la chaine 'Hello, World!'
    :rtype: String
    """
    return 'Hello, World!'


if __name__ == "__main__":
    # read server parameters
    params = config('./app/back/src/config.ini', 'server')
    #context = (params['cert'], params['key']) #certificate and key files
    # Launch Flask server
    app.run(debug=params['debug'], host=params['host'], port=params['port'])


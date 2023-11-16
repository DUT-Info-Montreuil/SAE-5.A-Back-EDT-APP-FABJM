#!/usr/bin/env python
# -*- coding: utf-8 -*-
# rest_api.py
import os

from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS
import json
import psycopg2
import requests
from contextlib import closing

from src.config import config
import src.connect_pg


app = Flask(__name__)
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
    """
    Cette fonction crée l'application

    :param parametre1: définit les options souhaité
    :type parametre1: dict
    :return: Renvoie l'application configurer
    :rtype: flask.app.Flask
    """
    
    app.config.from_object(config)
    return app
    
@app.route('/index')
def index():
    """
    Cette fonction permet de pinger l'application, elle sert de route Flask à l'adresse '/index'

    :return: Renvoie la chaine 'Hello, World!'
    :rtype: String
    """
    return 'Hello, World!'




if __name__ == "__main__":
    # read server parameters
    params = config('config.ini', 'server')
    #context = (params['cert'], params['key']) #certificate and key files
    # Launch Flask server
    app.run(debug=params['debug'], host=params['host'], port=params['port'])

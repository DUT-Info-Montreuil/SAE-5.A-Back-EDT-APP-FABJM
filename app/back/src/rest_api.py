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
from src.connect_pg import formatageSqlite3
import src.apiException as apiException
from datetime import timedelta
from src.routes.user_route import user
from src.routes.semestre_route import semestre
from src.routes.ressource_route import ressource
from src.routes.salle_route import salle
from src.routes.groupe_route import groupe
from src.routes.cours_route import cours

app = Flask(__name__)
"""JWT CONFIGURATION"""

secret_key = os.urandom(32)
app.config['SECRET_KEY'] = secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)

jwt = JWTManager(app)


"""Register blueprints"""
app.register_blueprint(user)
app.register_blueprint(cours)

app.register_blueprint(salle)
app.register_blueprint(semestre)
app.register_blueprint(ressource)

app.register_blueprint(groupe)


"""Variable représentant l'application web"""

CORS(app, origins=['http://localhost:4200'])


api = Api(app)



@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

def init_bdd(db_conn, chemin):
    """Initialise les table d'une base de donnée à partir d'un script

    :param db_conn: Connection à une base de donnée
    :type db_conn: Connexion
    
    :param chemin: chemin vers le script sql
    :type chemin: str
    """
    sql_file_path = os.path.dirname(os.path.dirname(os.getcwd())) + chemin
    sql_script = ""
    with open(sql_file_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        sql_script += formatageSqlite3(line)[0]
    db_cursor = db_conn.cursor()
    try:
        db_cursor.executescript(sql_script)
    except Exception as error:
        print("Exception : ", error)
    db_conn.commit()

def create_app(config):
    """Cette fonction crée l'application

    :param config: définit les options souhaité
    :type config: Objet
    
    :return:  l'application configurer
    :rtype: flask.app.Flask
    """
    
    app.config.update(config)
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


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
import src.connect_pg as connect_pg
import src.apiException as apiException


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


@app.route('/utilisateurs/get', methods=['GET','POST'])
def get_utilisateur():
    """Renvoit tout les utilisateurs via la route /utilisateurs/get
    
    :raises AucuneDonneeTrouverException: Aucune donnée n'a été trouvé dans la table utilisateur
    
    :return: une liste de tout les utilisateurs sous le format json
    :rtype: json
    """
    query = "SELECT * FROM utilisateur"

    conn = connect_pg.connect()

    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    
    try:
        for row in rows:
            returnStatement.append(get_utilisateur_statement(row))
    except(TypeError) as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("utilisateur"))}), 404
    
    connect_pg.disconnect(conn)

    return jsonify(returnStatement)
    
@app.route('/utilisateurs/get/<idUser>', methods=['GET','POST'])
def get_one_utilisateur(idUser):
    """Renvoit un utilisateur spécifié par son id via la route /utilisateurs/get<idUser>
    
    :param IdUtilisateur: id d'un utilisateur présent dans la base de donnée
    :type IdUtilisateur: Numérique
    
    :raises DonneeIntrouvableException: Impossible de trouver l'id spécifié dans la table utilisateur
    :raises ParamètreTypeInvalideException: Le type de l’id est invalide
    
    :return:  l'utilisateur a qui appartient cette id
    :rtype: json
    """
    query = "select * from utilisateur where IdUtilisateur=%(IdUtilisateur)s order by IdUtilisateur asc" % {'IdUtilisateur':idUser}

    conn = connect_pg.connect()

    rows = connect_pg.get_query(conn, query)

    returnStatement = {}
    
    if idUser.isdigit():
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idUser", "Numérique"))}), 400
    
    try:
        if len(rows) > 0:
            returnStatement = get_utilisateur_statement(rows[0])
    except(TypeError) as e:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("utilisateur", idUser))}), 404
    
    connect_pg.disconnect(conn)

    return jsonify(returnStatement)


@app.route('/utilisateurs/add', methods=['POST'])
def add_utilisateur():
    """Permet d'ajouter un utilisateur via la route /utilisateurs/add
    
    :param IdUtilisateur: donnée représentant un utilisateur
    :type IdUtilisateur: json
    
    :raises InsertionImpossibleException: Impossible d'ajouter l'utilisateur spécifié dans la table utilisateur
    
    :return: l'utilisateur qui vient d'être crée
    :rtype: json
    """
    returnStatement = []
    jsonObject = request.json
    for key, value in jsonObject.items():
        jsonObject[key] = value.replace("'", "''")
        
    insertColumns = ",".join(list(jsonObject.keys()))
    insertValues = "'" + "','".join(list(jsonObject.values())) + "'"
    query = "insert into utilisateur (%(columns)s) values (%(values)s) returning IdUtilisateur" % {'columns':insertColumns, 'values':insertValues}
    conn = connect_pg.connect()
    row = connect_pg.execute_commands(conn, (query,))
    try:
        if len(row) == 0:
            pass
    except(TypeError) as e:
        return jsonify({'error': str(apiException.InsertionImpossibleException("utilisateur"))}), 404
    connect_pg.disconnect(conn)
    return get_one_utilisateur(row)


def get_utilisateur_statement(row) :
    """ 
    Fonction de mappage de la table utilisateur
    
    :param row: donnée représentant un utilisateur
    :type row: tableau
    
    :return: les données représentant un utilisateur
    :rtype: dictionnaire
    """
    return {
        'IdUtilisateur':row[0],
        'FirstName':row[1],
        'LastName':row[2],
        'Username':row[3],
        'PassWord':row[4],
        'FirstLogin':row[5]
    }



if __name__ == "__main__":
    # read server parameters
    params = config('config.ini', 'server')
    #context = (params['cert'], params['key']) #certificate and key files
    # Launch Flask server
    app.run(debug=params['debug'], host=params['host'], port=params['port'])


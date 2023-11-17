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


@app.route('/utilisateurs/get', methods=['GET','POST'])
def get_utilisateur():
    """
	Renvoit tout les utilisateurs via la route /utilisateurs/get

	:return: Une revoit une liste de tout les utisatateurs sous le format json
	:rtype: json
	"""
    query = "SELECT * FROM utilisateur"

    conn = connect_pg.connect()

    rows = connect_pg.get_query(conn, query)

    returnStatement = []

    for row in rows:
        returnStatement.append(get_utilisateur_statement(row))
    
    connect_pg.disconnect(conn)

    return jsonify(returnStatement)
    
@app.route('/utilisateurs/get/<idUser>', methods=['GET','POST'])
def get_one_utilisateur(idUser):
    """
	Renvoit un utilisateur spécifié par son id via la route /utilisateurs/get<idUser>

	:param IdUtilisateur: id d'un utilisateur présant dans la base
	:type IdUtilisateur: int
	:return: renvoit l'utilisateur a qui appartient cette id
	:rtype: json
	:raises TypeError: Impossible de trouver l'id
	"""
    query = "select * from utilisateur where IdUtilisateur=%(IdUtilisateur)s order by IdUtilisateur asc" % {'IdUtilisateur':idUser}

    conn = connect_pg.connect()

    rows = connect_pg.get_query(conn, query)

    returnStatement = {}

    if len(rows) > 0:
        returnStatement = get_utilisateur_statement(rows[0])
    	
    
    connect_pg.disconnect(conn)

    return jsonify(returnStatement)


@app.route('/utilisateurs/add', methods=['POST'])
def add_utilisateur():
	"""
	Permet d'ajouter un utilisateur via la route /utilisateurs/add

	:return: renvoit l'utilisateur qui vient d'être crée
	:rtype: json
	"""
	returnStatement = []
	jsonObject = request.json
	# we escape all values
	
	for key, value in jsonObject.items():
		jsonObject[key] = value.replace("'", "''")
	# For each column, we add an SQL column and value => table1,table2,table3... / 'value1','value2','value3'...
	insertColumns = ",".join(list(jsonObject.keys()))
	insertValues = "'" + "','".join(list(jsonObject.values())) + "'"
	# we build the insert query
	query = "insert into utilisateur (%(columns)s) values (%(values)s) returning IdUtilisateur" % {'columns':insertColumns, 'values':insertValues}
	conn = connect_pg.connect()
	# the query returning the book id
	row = connect_pg.execute_commands(conn, (query,))
	connect_pg.disconnect(conn)
	# finally, we return the book
	return get_one_utilisateur(row)


def get_utilisateur_statement(row) :
    """ Book array statement """
    return {
        'IdUtilisateur':row[0],
        'FirstName':row[1],
        'LastName':row[2],
        'Username':row[3],
        'PassWord':row[4],
        'FirstLogin': row[5],
    }



if __name__ == "__main__":
    # read server parameters
    params = config('config.ini', 'server')
    context = (params['cert'], params['key']) #certificate and key files
    # Launch Flask server
    app.run(debug=params['debug'], host=params['host'], port=params['port'], ssl_context=context)

